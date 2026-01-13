package main

import (
	"context"
	"net/http"
	"os"
	"os/signal"
	"sync"
	"syscall"
	"time"

	"github.com/prometheus/client_golang/prometheus/promhttp"
	"github.com/smartfactory/stream-gateway/internal/api"
	"github.com/smartfactory/stream-gateway/internal/capture"
	"github.com/smartfactory/stream-gateway/internal/config"
	"github.com/smartfactory/stream-gateway/internal/grpc"
	"github.com/smartfactory/stream-gateway/internal/logger"
	"github.com/smartfactory/stream-gateway/internal/metrics"
	"github.com/smartfactory/stream-gateway/internal/websocket"
	"go.uber.org/zap"
)

func main() {
	cfg := config.Load()

	log := logger.New(cfg.LogLevel)
	defer log.Sync()

	log.Info("starting stream gateway",
		zap.String("version", "2.0.0"),
		zap.String("ai_engine", cfg.AIEngineURL),
	)

	metrics.Init()

	hub := websocket.NewHub()
	go hub.Run()

	grpcClient, err := grpc.NewInferenceClient(cfg.AIEngineURL)
	if err != nil {
		log.Warn("AI engine not available via gRPC, running in standalone mode", zap.Error(err))
		grpcClient = nil
	}
	if grpcClient != nil {
		defer grpcClient.Close()
	}

	cameraManager := capture.NewManager(log)

	processor := NewProcessor(cfg, log, hub, grpcClient, cameraManager)

	router := api.NewRouter(log, hub, cameraManager, processor)

	httpServer := &http.Server{
		Addr:    cfg.HTTPAddr,
		Handler: router,
	}

	metricsServer := &http.Server{
		Addr:    cfg.MetricsAddr,
		Handler: promhttp.Handler(),
	}

	var wg sync.WaitGroup

	wg.Add(1)
	go func() {
		defer wg.Done()
		log.Info("HTTP server starting", zap.String("addr", cfg.HTTPAddr))
		if err := httpServer.ListenAndServe(); err != http.ErrServerClosed {
			log.Error("HTTP server error", zap.Error(err))
		}
	}()

	wg.Add(1)
	go func() {
		defer wg.Done()
		log.Info("metrics server starting", zap.String("addr", cfg.MetricsAddr))
		if err := metricsServer.ListenAndServe(); err != http.ErrServerClosed {
			log.Error("metrics server error", zap.Error(err))
		}
	}()

	wg.Add(1)
	go func() {
		defer wg.Done()
		processor.Start()
	}()

	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	log.Info("shutting down...")

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	processor.Stop()
	httpServer.Shutdown(ctx)
	metricsServer.Shutdown(ctx)

	wg.Wait()
	log.Info("shutdown complete")
}

type Processor struct {
	cfg           *config.Config
	log           *zap.Logger
	hub           *websocket.Hub
	grpcClient    *grpc.InferenceClient
	cameraManager *capture.Manager
	running       bool
	stopChan      chan struct{}
	mu            sync.RWMutex
}

func NewProcessor(
	cfg *config.Config,
	log *zap.Logger,
	hub *websocket.Hub,
	grpcClient *grpc.InferenceClient,
	cameraManager *capture.Manager,
) *Processor {
	return &Processor{
		cfg:           cfg,
		log:           log,
		hub:           hub,
		grpcClient:    grpcClient,
		cameraManager: cameraManager,
		stopChan:      make(chan struct{}),
	}
}

func (p *Processor) Start() {
	p.mu.Lock()
	p.running = true
	p.mu.Unlock()

	ticker := time.NewTicker(time.Duration(1000/p.cfg.TargetFPS) * time.Millisecond)
	defer ticker.Stop()

	p.log.Info("processor started", zap.Int("target_fps", p.cfg.TargetFPS))

	for {
		select {
		case <-ticker.C:
			p.processFrames()
		case <-p.stopChan:
			p.log.Info("processor stopped")
			return
		}
	}
}

func (p *Processor) Stop() {
	p.mu.Lock()
	p.running = false
	p.mu.Unlock()
	close(p.stopChan)
}

func (p *Processor) processFrames() {
	if p.grpcClient == nil {
		return
	}
	
	cameras := p.cameraManager.GetActiveCameras()

	for _, cam := range cameras {
		frame, ok := cam.GetLatestFrame()
		if !ok {
			continue
		}

		startTime := time.Now()

		result, err := p.grpcClient.Detect(frame, cam.ID, p.cfg.ConfidenceThreshold)
		if err != nil {
			p.log.Warn("detection failed",
				zap.String("camera", cam.ID),
				zap.Error(err),
			)
			metrics.RecordError("detection")
			continue
		}

		processingTime := time.Since(startTime)
		metrics.RecordInference(processingTime.Seconds())
		metrics.RecordDetections(len(result.Detections))

		message := websocket.Message{
			Type:      "detection",
			CameraID:  cam.ID,
			Timestamp: time.Now().UnixMilli(),
			Data:      result,
		}

		p.hub.Broadcast(message)

		if result.SafetyCheck.HasViolations {
			metrics.RecordViolation()
			p.log.Warn("safety violation detected",
				zap.String("camera", cam.ID),
				zap.Strings("violations", result.SafetyCheck.Violations),
			)
		}
	}
}

func (p *Processor) IsRunning() bool {
	p.mu.RLock()
	defer p.mu.RUnlock()
	return p.running
}
