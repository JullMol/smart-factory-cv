# RTSP Stream Simulation Guide

Complete guide for testing Smart Factory CV with realistic CCTV streams.

## Prerequisites

1. **Docker Desktop** - [Download](https://www.docker.com/products/docker-desktop/)
2. **FFmpeg** - [Download](https://ffmpeg.org/download.html)
3. **Sample Videos** - Factory/construction CCTV footage

---

## Quick Start

### Step 1: Start MediaMTX RTSP Server

```powershell
cd deploy
docker-compose -f docker-compose.rtsp.yml up -d
```

The RTSP server will be available at `rtsp://localhost:8554`

### Step 2: Add Sample Videos

Place your videos in `services/dashboard/public/videos/` with names:
- `cam1.mp4` - Main Entrance
- `cam2.mp4` - Assembly Line
- `cam3.mp4` - Loading Dock
- `cam4.mp4` - Machine Shop

### Step 3: Stream Videos to RTSP

```powershell
cd deploy
.\stream-videos.bat
```

This will stream each video to the RTSP server.

### Step 4: Enable RTSP Mode in Dashboard

Create `.env` file in `services/dashboard/`:

```env
VITE_USE_RTSP=true
VITE_RTSP_SERVER=localhost:8888
VITE_AI_API_URL=http://localhost:8000
```

### Step 5: Run Full System

```powershell
.\start.ps1
```

---

## Manual FFmpeg Streaming

Stream a single video:

```bash
ffmpeg -re -stream_loop -1 -i video.mp4 -c copy -f rtsp rtsp://localhost:8554/live/cam1
```

Parameters:
- `-re` - Read at native frame rate
- `-stream_loop -1` - Loop forever
- `-c copy` - No re-encoding (fast)
- `-f rtsp` - Output format

---

## Verify Streams

Test with FFplay:

```bash
ffplay rtsp://localhost:8554/live/cam1
```

Or open in VLC: `rtsp://localhost:8554/live/cam1`

---

## Architecture

```
┌─────────────────┐     ┌─────────────────┐
│ Sample Videos   │────▶│ MediaMTX        │
│ (cam1-4.mp4)    │     │ RTSP Server     │
└─────────────────┘     │ :8554           │
                        └────────┬────────┘
                                 │ HLS/WebRTC
                                 ▼
┌─────────────────┐     ┌─────────────────┐
│ AI Inference    │◀────│ Dashboard       │
│ :8000           │     │ :3000           │
└─────────────────┘     └─────────────────┘
```

---

## Troubleshooting

### Video not streaming
- Check FFmpeg is installed: `ffmpeg -version`
- Check MediaMTX is running: `docker ps`
- Verify video file path

### No detection
- Ensure AI service is running: `http://localhost:8000/health`
- Check browser console for errors
- Try fallback mode (disable RTSP)

### High latency
- MediaMTX HLS has ~3-5s delay
- For lower latency, use WebRTC (port 8889)
