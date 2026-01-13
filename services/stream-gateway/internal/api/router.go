package api

import (
	"encoding/json"
	"net/http"

	"github.com/smartfactory/stream-gateway/internal/capture"
	"github.com/smartfactory/stream-gateway/internal/websocket"
	"go.uber.org/zap"
)

type Processor interface {
	IsRunning() bool
}

func NewRouter(
	log *zap.Logger,
	hub *websocket.Hub,
	cameraManager *capture.Manager,
	processor Processor,
) http.Handler {
	mux := http.NewServeMux()

	mux.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(map[string]interface{}{
			"status":     "healthy",
			"processing": processor.IsRunning(),
			"clients":    hub.ClientCount(),
		})
	})

	mux.HandleFunc("/ws", func(w http.ResponseWriter, r *http.Request) {
		websocket.ServeWs(hub, w, r)
	})

	mux.HandleFunc("/api/cameras", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")

		switch r.Method {
		case http.MethodGet:
			cameras := cameraManager.GetAllCameras()
			json.NewEncoder(w).Encode(cameras)

		case http.MethodPost:
			var cfg capture.CameraConfig
			if err := json.NewDecoder(r.Body).Decode(&cfg); err != nil {
				http.Error(w, err.Error(), http.StatusBadRequest)
				return
			}

			if err := cameraManager.AddCamera(cfg); err != nil {
				http.Error(w, err.Error(), http.StatusInternalServerError)
				return
			}

			log.Info("camera created via API", zap.String("id", cfg.ID))
			w.WriteHeader(http.StatusCreated)
			json.NewEncoder(w).Encode(map[string]string{"status": "created", "id": cfg.ID})

		default:
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		}
	})

	mux.HandleFunc("/api/cameras/", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")

		cameraID := r.URL.Path[len("/api/cameras/"):]
		if cameraID == "" {
			http.Error(w, "Camera ID required", http.StatusBadRequest)
			return
		}

		switch r.Method {
		case http.MethodGet:
			cam, exists := cameraManager.GetCamera(cameraID)
			if !exists {
				http.Error(w, "Camera not found", http.StatusNotFound)
				return
			}
			json.NewEncoder(w).Encode(cam)

		case http.MethodDelete:
			if !cameraManager.RemoveCamera(cameraID) {
				http.Error(w, "Camera not found", http.StatusNotFound)
				return
			}
			log.Info("camera deleted via API", zap.String("id", cameraID))
			json.NewEncoder(w).Encode(map[string]string{"status": "deleted"})

		default:
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		}
	})

	mux.HandleFunc("/api/cameras/start/", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
			return
		}

		cameraID := r.URL.Path[len("/api/cameras/start/"):]
		if err := cameraManager.StartCamera(cameraID); err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}

		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(map[string]string{"status": "started"})
	})

	mux.HandleFunc("/api/cameras/stop/", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
			return
		}

		cameraID := r.URL.Path[len("/api/cameras/stop/"):]
		if err := cameraManager.StopCamera(cameraID); err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}

		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(map[string]string{"status": "stopped"})
	})

	return corsMiddleware(mux)
}

func corsMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Access-Control-Allow-Origin", "*")
		w.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
		w.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization")

		if r.Method == http.MethodOptions {
			w.WriteHeader(http.StatusNoContent)
			return
		}

		next.ServeHTTP(w, r)
	})
}
