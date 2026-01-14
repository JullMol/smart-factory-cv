# 🏭 Smart Factory CV

### ⚡ AI-Powered Industrial Safety Monitoring System ⚡

A real-time computer vision system that monitors factory environments for **PPE compliance** and safety violations using YOLOv8 and modern web technologies.

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Architecture](#️-architecture) • [Tech Stack](#-tech-stack) • [Contributing](#-contributing)

---

## 🎯 Overview

Smart Factory CV is an **industrial-grade safety monitoring solution** that uses computer vision to detect Personal Protective Equipment (PPE) violations in real-time. The system monitors camera feeds, runs AI inference, and provides instant visual feedback through a modern dashboard.

Built with a **futuristic industrial aesthetic** featuring glassmorphism UI, real-time video processing, and intelligent alerting.

---

## ✨ Features

### 📹 Multi-Camera Monitoring
- Real-time video feed processing
- Support for multiple camera sources
- Live detection overlay with bounding boxes
- Per-camera compliance metrics

### 🤖 AI-Powered Detection
- YOLOv8 ONNX inference engine
- PPE detection (Hardhat, Safety Vest, Mask)
- Violation detection (NO-Hardhat, NO-Safety Vest, NO-Mask)
- Configurable confidence threshold

### 📊 Real-time Dashboard
- Modern dark theme industrial UI
- Live camera grid with detection overlays
- System metrics (latency, people count, compliance rate)
- Safety alerts with violation history

### ⚡ High Performance
- Optimized ONNX Runtime inference
- FastAPI backend with async processing
- React frontend with smooth animations
- Low-latency video processing

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        🖥️ Dashboard (React)                     │
│                    Modern Industrial UI + Charts                │
└─────────────────────────────────┬───────────────────────────────┘
                                  │ HTTP/REST
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                     🧠 AI Inference (Python)                     │
│                   FastAPI + YOLOv8 + ONNX Runtime               │
└─────────────────────────────────────────────────────────────────┘
                                  │
            ┌─────────────────────┼─────────────────────┐
            ▼                     ▼                     ▼
    ┌───────────────┐    ┌───────────────┐    ┌───────────────┐
    │   Detector    │    │  Safety Check │    │    Alerts     │
    │  YOLOv8 ONNX  │    │ PPE Compliance│    │  Violations   │
    └───────────────┘    └───────────────┘    └───────────────┘
```

---

## 🔧 Installation

### Prerequisites
- Python 3.10+
- Node.js 18+
- Git

### Quick Setup

```bash
# Clone the repository
git clone https://github.com/JullMol/smart-factory-cv.git
cd smart-factory-cv

# Setup AI Inference
cd services/ai-inference
pip install -r requirements.txt

# Setup Dashboard
cd ../dashboard
npm install
```

---

## 🚀 Usage

### 1️⃣ Start AI Inference Server

```bash
cd services/ai-inference
python src/main.py
```

Server runs at `http://localhost:8000`

### 2️⃣ Start Dashboard

```bash
cd services/dashboard
npm run dev
```

Dashboard runs at `http://localhost:3000`

### 3️⃣ Access Dashboard

Open your browser and navigate to `http://localhost:3000` to view the monitoring dashboard.

---

## 🔌 API Reference

### Health Check
```http
GET /health
```
Returns server status and model information.

### Detection Endpoint
```http
POST /detect
Content-Type: multipart/form-data

file: image/jpeg
confidence: 0.5 (optional)
```

Returns:
```json
{
  "detections": [
    {
      "class_name": "Hardhat",
      "confidence": 0.95,
      "bbox": [x1, y1, x2, y2]
    }
  ],
  "safety_check": {
    "people_count": 2,
    "violation_count": 1,
    "compliance_rate": 50,
    "has_violations": true,
    "violations": ["NO-Mask"]
  },
  "processing_time_ms": 32.5
}
```

---

## 📁 Project Structure

```
smart-factory-cv/
├── 📂 services/
│   ├── 📂 ai-inference/          # Python AI Backend
│   │   ├── src/
│   │   │   ├── main.py           # FastAPI server entry
│   │   │   ├── detector.py       # ONNX detector
│   │   │   └── config.py         # Configuration
│   │   ├── models/               # ONNX model files
│   │   └── requirements.txt
│   │
│   └── 📂 dashboard/             # React Frontend
│       ├── src/
│       │   ├── App.jsx           # Main component
│       │   ├── components/       # UI components
│       │   └── styles/           # CSS styles
│       └── package.json
│
├── 📂 deploy/                    # Deployment configs
│   └── mediamtx.yml              # MediaMTX streaming config
│
├── 📂 data/                      # Training datasets
│
├── Makefile                      # Build commands
└── README.md                     # This file
```

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **AI Engine** | Python, YOLOv8, ONNX Runtime, FastAPI |
| **Frontend** | React 18, Vite, Zustand, Recharts |
| **Model** | YOLOv8n Custom (71.7% mAP50) |
| **Styling** | CSS3 with Glassmorphism |

---

## 📊 Model Performance

| Metric | Value |
|--------|-------|
| **Model** | YOLOv8n Custom |
| **mAP50** | 71.7% |
| **Inference** | ~30ms (CPU) |
| **Model Size** | 6.3MB |
| **Classes** | 6 (Hardhat, Safety Vest, Mask + NO variants) |

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork** the repository
2. **Create** a feature branch
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Commit** your changes
   ```bash
   git commit -m 'Add amazing feature'
   ```
4. **Push** to the branch
   ```bash
   git push origin feature/amazing-feature
   ```
5. **Open** a Pull Request

### Ideas for Contributions
- 🎨 UI/UX improvements
- 🧠 Model optimization
- 📊 Additional metrics and charts
- 🔧 Performance optimizations
- 📝 Documentation improvements

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

### 🌟 Star this repo if you find it useful!

**Made with ❤️ for industrial safety**

</div>
