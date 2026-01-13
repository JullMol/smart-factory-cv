# Smart Factory CV

**Industry-Grade AI-Powered PPE Detection System for Industrial Safety Monitoring**

Real-time computer vision system that monitors factory floors for PPE compliance, detects safety violations, and provides intelligent alerting through virtual fencing zones.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Go](https://img.shields.io/badge/Go-1.21+-00ADD8?logo=go)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python)
![React](https://img.shields.io/badge/React-18+-61DAFB?logo=react)

## Features

- **Real-time Detection**: ONNX/TensorRT optimized YOLOv8 inference (<10ms latency)
- **Multi-Camera Support**: Manage 8+ RTSP/webcam streams concurrently
- **Virtual Fencing**: Define polygon danger zones with custom PPE requirements
- **Object Tracking**: Person re-identification across frames with ByteTrack
- **gRPC Communication**: High-performance binary protocol between services
- **Industrial Dashboard**: Dark theme UI with live camera grid and alert panel
- **Observability**: Prometheus metrics + Grafana dashboards
- **One-Command Deploy**: Docker Compose with GPU support

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   RTSP/Webcam   │────▶│  Stream Gateway  │────▶│    Dashboard    │
│    Cameras      │     │      (Go)        │     │    (React)      │
└─────────────────┘     └────────┬─────────┘     └─────────────────┘
                                 │ gRPC
                        ┌────────▼─────────┐
                        │   AI Inference   │
                        │ (Python + ONNX)  │
                        └──────────────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        ▼                        ▼                        ▼
┌───────────────┐    ┌───────────────────┐    ┌────────────────┐
│   Detector    │    │     Tracker       │    │  Zone Checker  │
│ YOLOv8 ONNX   │    │  Object Re-ID     │    │Virtual Fencing │
└───────────────┘    └───────────────────┘    └────────────────┘
```

## Quick Start

### Prerequisites

- Docker & Docker Compose
- NVIDIA GPU + CUDA (optional, for TensorRT)
- Node.js 18+ (for local development)
- Go 1.21+ (for local development)
- Python 3.10+ (for local development)

### One-Command Deployment

```bash
docker-compose -f deploy/docker-compose.yml up -d
```

Access:
- **Dashboard**: http://localhost:3000
- **API**: http://localhost:8080
- **Grafana**: http://localhost:3001 (admin/smartfactory)
- **Prometheus**: http://localhost:9092

### Local Development

```bash
# Install dependencies
make dev
```

## Project Structure

```
smart-factory-cv/
├── services/
│   ├── ai-inference/         # Python - ONNX/TensorRT detector
│   │   ├── src/              # Main server, detector, tracker, zones
│   │   ├── scripts/          # Model export, training
│   │   └── Dockerfile
│   ├── stream-gateway/       # Go - RTSP capture, WebSocket hub
│   │   ├── cmd/server/       # Entry point
│   │   ├── internal/         # Core packages
│   │   └── Dockerfile
│   └── dashboard/            # React - Industrial UI
│       ├── src/              # Components, hooks, store
│       └── Dockerfile
├── proto/                    # gRPC definitions
├── deploy/                   # Docker Compose
├── monitoring/               # Prometheus + Grafana
└── docs/                     # Documentation
```

## Tech Stack

| Component | Technology |
|-----------|------------|
| AI Engine | Python, ONNX Runtime, TensorRT, Norfair, Shapely |
| Backend | Go, gRPC, WebSocket, Prometheus |
| Frontend | React 18, Recharts, Framer Motion, Zustand |
| Infrastructure | Docker, Redis, Prometheus, Grafana |
| Model | YOLOv8n (71.7% mAP50, 6.3MB) |

## Configuration

### Environment Variables

**AI Inference:**
```env
MODEL_PATH=/app/models/best.onnx
CONFIDENCE_THRESHOLD=0.5
GRPC_PORT=50051
DEVICE=cuda
```

**Stream Gateway:**
```env
AI_ENGINE_URL=ai-inference:50051
HTTP_ADDR=:8080
TARGET_FPS=15
```

### Zone Configuration

Define danger zones in `services/ai-inference/config/zones.yaml`:

```yaml
zones:
  - id: "zone-1"
    name: "Machine Area"
    severity: "danger"
    required_ppe:
      - "Hardhat"
      - "Safety Vest"
    polygon:
      - { x: 100, y: 100 }
      - { x: 400, y: 100 }
      - { x: 400, y: 400 }
      - { x: 100, y: 400 }
```

## API Reference

### REST Endpoints (Stream Gateway)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/api/cameras` | List all cameras |
| POST | `/api/cameras` | Add camera |
| POST | `/api/cameras/start/:id` | Start camera stream |
| WS | `/ws` | WebSocket for real-time updates |

### gRPC Methods (AI Inference)

| Method | Description |
|--------|-------------|
| `Detect` | Single image detection |
| `StreamDetect` | Streaming detection |
| `HealthCheck` | Service health |

## Model Export

Export YOLOv8 to optimized formats:

```bash
# ONNX export
python services/ai-inference/scripts/export_model.py onnx --model models/best.pt

# TensorRT FP16
python services/ai-inference/scripts/export_model.py tensorrt --model models/best.pt --half

# Benchmark
python services/ai-inference/scripts/export_model.py benchmark
```

## Performance

| Metric | Value |
|--------|-------|
| Inference (TensorRT FP16) | <10ms |
| gRPC Latency | <5ms |
| WebSocket Broadcast | <2ms |
| Multi-Camera Support | 8+ streams |
| Model Size | 6.3MB |

## License

MIT
