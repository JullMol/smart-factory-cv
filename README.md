# Smart Factory CV

AI-powered PPE detection system for industrial safety monitoring using YOLOv8.

## Features

- Real-time webcam detection
- Image upload for batch processing
- RTSP stream support (for IP cameras)
- Safety violation tracking
- Live dashboard with detection stats

## Tech Stack

- **AI Engine**: Python 3.10+, YOLOv8, FastAPI
- **Backend**: Go 1.21+, WebSocket streaming
- **Frontend**: React 18, Vite
- **Model**: YOLOv8n (71.7% mAP50, 6.3MB)

## Quick Start

### Prerequisites

- Python 3.10+
- Go 1.21+
- Node.js 18+
- NVIDIA GPU (optional, for training)

### Installation

```powershell
.\setup.ps1
```

### Running

```powershell
.\start.ps1
```

Access dashboard at: http://localhost:3000

## Project Structure

```
smart-factory-cv/
├── ai-engine/
│   ├── src/              # FastAPI server & detector
│   ├── scripts/          # Training scripts
│   ├── models/           # Trained models (best.pt)
│   └── requirements.txt  # Python dependencies
├── backend-streamer/
│   ├── cmd/              # Main entry point
│   ├── internal/         # WebSocket & stream processing
│   └── go.mod            # Go dependencies
├── frontend-dashboard/
│   ├── src/              # React components
│   ├── package.json      # Node dependencies
│   └── vite.config.js    # Vite configuration
├── data/
│   └── merged_dataset/   # Training dataset (9,442 images)
├── setup.ps1             # Dependency installer
├── start.ps1             # Service launcher
├── README.md
└── .gitignore
```

## API Endpoints

### AI Engine (port 8000)
- `GET /health` - Health check
- `POST /detect` - Detect objects in image
- `POST /detect/base64` - Detect objects in base64 image

### Backend (port 8080)
- `GET /health` - Health check
- `WS /ws` - WebSocket for real-time detections

## Training

Train custom model:

```powershell
cd ai-engine/scripts
python train.py --model n --epochs 100 --batch 16 --device 0
```

Options:
- `--model`: n, s, m, l, x (model size)
- `--epochs`: training epochs
- `--batch`: batch size
- `--device`: 0 (GPU) or cpu

## Dataset

- **Classes**: Hardhat, Mask, NO-Hardhat, NO-Mask, NO-Safety Vest, Person, Safety Cone, Safety Vest, machinery, vehicle
- **Images**: 9,442 (7,254 train, 1,442 val, 746 test)
- **Format**: YOLO (normalized bounding boxes)

## Model Performance

- **mAP50**: 71.7%
- **mAP50-95**: 48.1%
- **Inference**: 2.1ms (RTX 4050)
- **Size**: 6.3MB

## License

MIT
