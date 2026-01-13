import express from 'express';
import { readdirSync, statSync, watchFile } from 'fs';
import { join, extname } from 'path';
import cors from 'cors';

const app = express();
const PORT = 3002;
const VIDEOS_DIR = join(process.cwd(), 'public', 'videos');

app.use(cors());

const VIDEO_EXTENSIONS = ['.mp4', '.webm', '.ogg', '.mov', '.avi'];

function scanVideos() {
  try {
    const files = readdirSync(VIDEOS_DIR);
    const videos = files
      .filter(file => VIDEO_EXTENSIONS.includes(extname(file).toLowerCase()))
      .map((file, index) => {
        const stats = statSync(join(VIDEOS_DIR, file));
        return {
          id: `cam-${index + 1}`,
          name: file.replace(/\.[^/.]+$/, '').replace(/[-_]/g, ' '),
          filename: file,
          url: `/videos/${file}`,
          size: stats.size,
          modified: stats.mtime
        };
      });
    return videos;
  } catch (e) {
    console.log('Videos folder not found or empty');
    return [];
  }
}

app.get('/api/videos', (req, res) => {
  const videos = scanVideos();
  res.json({
    count: videos.length,
    videos
  });
});

app.get('/api/videos/watch', (req, res) => {
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');
  
  const sendUpdate = () => {
    const videos = scanVideos();
    res.write(`data: ${JSON.stringify({ videos })}\n\n`);
  };
  
  sendUpdate();
  const interval = setInterval(sendUpdate, 5000);
  
  req.on('close', () => {
    clearInterval(interval);
  });
});

app.listen(PORT, () => {
  console.log(`Video API running on http://localhost:${PORT}`);
  console.log(`Watching: ${VIDEOS_DIR}`);
});
