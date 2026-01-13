package metrics

import (
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promauto"
)

var (
	framesProcessed = promauto.NewCounter(prometheus.CounterOpts{
		Name: "gateway_frames_processed_total",
		Help: "Total number of frames processed",
	})

	inferenceLatency = promauto.NewHistogram(prometheus.HistogramOpts{
		Name:    "gateway_inference_latency_seconds",
		Help:    "Time spent waiting for AI inference",
		Buckets: []float64{0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0},
	})

	detectionsTotal = promauto.NewCounter(prometheus.CounterOpts{
		Name: "gateway_detections_total",
		Help: "Total number of detections received",
	})

	violationsTotal = promauto.NewCounter(prometheus.CounterOpts{
		Name: "gateway_violations_total",
		Help: "Total number of safety violations detected",
	})

	errorsTotal = promauto.NewCounterVec(prometheus.CounterOpts{
		Name: "gateway_errors_total",
		Help: "Total number of errors by type",
	}, []string{"type"})

	activeCameras = promauto.NewGauge(prometheus.GaugeOpts{
		Name: "gateway_active_cameras",
		Help: "Number of currently active cameras",
	})

	wsClients = promauto.NewGauge(prometheus.GaugeOpts{
		Name: "gateway_websocket_clients",
		Help: "Number of connected WebSocket clients",
	})
)

func Init() {}

func RecordInference(duration float64) {
	framesProcessed.Inc()
	inferenceLatency.Observe(duration)
}

func RecordDetections(count int) {
	detectionsTotal.Add(float64(count))
}

func RecordViolation() {
	violationsTotal.Inc()
}

func RecordError(errorType string) {
	errorsTotal.WithLabelValues(errorType).Inc()
}

func SetActiveCameras(count int) {
	activeCameras.Set(float64(count))
}

func SetWSClients(count int) {
	wsClients.Set(float64(count))
}
