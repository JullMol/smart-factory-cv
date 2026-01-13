package main

import (
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"

	"github.com/yourusername/smart-factory-cv/backend-streamer/internal/stream"
	"github.com/yourusername/smart-factory-cv/backend-streamer/internal/websocket"
)

func main() {
	rtspURL := getEnv("RTSP_URL", "rtsp://localhost:8554/stream")
	aiEngineURL := getEnv("AI_ENGINE_URL", "http://localhost:8000")
	wsPort := getEnv("WS_PORT", ":8080")

	hub := websocket.NewHub()
	go hub.Run()

	processor := stream.NewProcessor(rtspURL, aiEngineURL, hub)
	go processor.Start()

	http.HandleFunc("/ws", func(w http.ResponseWriter, r *http.Request) {
		websocket.ServeWs(hub, w, r)
	})

	http.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		w.Write([]byte(`{"status":"healthy"}`))
	})

	server := &http.Server{
		Addr: wsPort,
	}

	go func() {
		if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("Server error: %v\n", err)
		}
	}()

	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	processor.Stop()
	server.Close()
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}
