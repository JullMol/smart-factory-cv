package config

import (
	"os"
	"strconv"
)

type Config struct {
	AIEngineURL         string
	HTTPAddr            string
	MetricsAddr         string
	LogLevel            string
	TargetFPS           int
	ConfidenceThreshold float32
	MaxCameras          int
	BufferSize          int
	ReconnectDelay      int
	GRPCTimeout         int
}

func Load() *Config {
	return &Config{
		AIEngineURL:         getEnv("AI_ENGINE_URL", "localhost:50051"),
		HTTPAddr:            getEnv("HTTP_ADDR", ":8080"),
		MetricsAddr:         getEnv("METRICS_ADDR", ":9091"),
		LogLevel:            getEnv("LOG_LEVEL", "info"),
		TargetFPS:           getEnvInt("TARGET_FPS", 15),
		ConfidenceThreshold: float32(getEnvFloat("CONFIDENCE_THRESHOLD", 0.5)),
		MaxCameras:          getEnvInt("MAX_CAMERAS", 16),
		BufferSize:          getEnvInt("BUFFER_SIZE", 30),
		ReconnectDelay:      getEnvInt("RECONNECT_DELAY_MS", 3000),
		GRPCTimeout:         getEnvInt("GRPC_TIMEOUT_MS", 5000),
	}
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

func getEnvInt(key string, defaultValue int) int {
	if value := os.Getenv(key); value != "" {
		if i, err := strconv.Atoi(value); err == nil {
			return i
		}
	}
	return defaultValue
}

func getEnvFloat(key string, defaultValue float64) float64 {
	if value := os.Getenv(key); value != "" {
		if f, err := strconv.ParseFloat(value, 64); err == nil {
			return f
		}
	}
	return defaultValue
}
