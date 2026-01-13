# Sample Video Download Guide

Download free factory/construction CCTV footage for testing PPE detection.

## Quick Download Links (Free & Royalty-Free)

### 1. Vecteezy (Recommended)
Free HD videos with workers wearing PPE:

- **Safety Gear Videos:** https://www.vecteezy.com/free-videos/safety-gear
- **Protective Equipment:** https://www.vecteezy.com/free-videos/protective-equipment  
- **Industry Safety:** https://www.vecteezy.com/free-videos/industry-safety
- **Safety Helmet:** https://www.vecteezy.com/free-videos/safety-helmet
- **Safety Vest:** https://www.vecteezy.com/free-videos/safety-vest

### 2. Freepik
- **Construction PPE:** https://www.freepik.com/videos/search?format=search&last_filter=query&last_value=construction+ppe&query=construction+ppe

### 3. Pexels (100% Free)
- **Construction Workers:** https://www.pexels.com/search/videos/construction%20workers/
- **Factory Workers:** https://www.pexels.com/search/videos/factory%20workers/
- **Warehouse:** https://www.pexels.com/search/videos/warehouse/

---

## Download Instructions

1. Go to one of the links above
2. Find a video with:
   - Workers wearing/not wearing helmets
   - Workers wearing/not wearing safety vests
   - Top-down or angled camera view (like CCTV)
3. Click Download (choose 1080p or 720p)
4. Rename to `cam1.mp4`, `cam2.mp4`, etc.
5. Move to `services/dashboard/public/videos/`

---

## Ideal Video Characteristics

| Criteria | What to Look For |
|----------|-----------------|
| Content | Workers with & without PPE |
| Angle | Top-down, angled (CCTV-style) |
| Duration | 30-60 seconds (will loop) |
| Resolution | 720p or 1080p |
| Format | MP4 (H.264) |

---

## YouTube Alternative (yt-dlp)

If you prefer YouTube videos:

```powershell
# Install yt-dlp
pip install yt-dlp

# Download video (example)
yt-dlp -f "best[height<=720]" -o "cam1.mp4" "VIDEO_URL"
```

Search YouTube for:
- "construction site safety video"
- "PPE awareness video factory"
- "industrial safety CCTV"

---

## After Download

```powershell
# Your video folder should look like:
services/dashboard/public/videos/
  ├── cam1.mp4  # Main Entrance
  ├── cam2.mp4  # Assembly Line
  ├── cam3.mp4  # Loading Dock
  └── cam4.mp4  # Machine Shop
```

Then run the RTSP simulation:
```powershell
cd deploy
docker-compose -f docker-compose.rtsp.yml up -d
.\stream-videos.bat
```
