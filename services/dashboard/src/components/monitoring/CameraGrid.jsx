import React, { useRef, useEffect, useState, useCallback } from 'react';
import useStore from '../../store/store';

const AI_API_URL = import.meta.env.VITE_AI_API_URL || 'http://localhost:8000';
const VIDEO_API_URL = import.meta.env.VITE_VIDEO_API_URL || 'http://localhost:3002';

const DEFAULT_VIDEOS = [
  { id: 'cam-1', name: 'Main Entrance', url: 'https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerMeltdowns.mp4' },
  { id: 'cam-2', name: 'Assembly Line A', url: 'https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerJoyrides.mp4' },
  { id: 'cam-3', name: 'Loading Dock', url: 'https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4' },
  { id: 'cam-4', name: 'Machine Shop', url: 'https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4' }
];

export default function CameraGrid() {
  const { cameras, detections } = useStore();
  const [videoList, setVideoList] = useState(DEFAULT_VIDEOS);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    const fetchVideos = async () => {
      try {
        const res = await fetch(`${VIDEO_API_URL}/api/videos`);
        if (res.ok) {
          const data = await res.json();
          if (data.videos && data.videos.length > 0) {
            setVideoList(data.videos);
          }
        }
      } catch (e) {
        console.log('Using default videos (API not available)');
      }
      setLoading(false);
    };
    
    fetchVideos();
    
    const eventSource = new EventSource(`${VIDEO_API_URL}/api/videos/watch`);
    eventSource.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data);
        if (data.videos && data.videos.length > 0) {
          setVideoList(data.videos);
        }
      } catch (err) {}
    };
    
    eventSource.onerror = () => {
      eventSource.close();
    };
    
    return () => eventSource.close();
  }, []);
  
  const displayCameras = cameras.length > 0 ? cameras : videoList;
  
  return (
    <div className="card" style={{ flex: 1 }}>
      <div className="card-header">
        <span className="card-title">Live Camera Feeds</span>
        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          {loading && (
            <span style={{ fontSize: '0.7rem', color: 'var(--accent-yellow)' }}>
              Loading...
            </span>
          )}
          <span style={{ 
            fontSize: '0.75rem', 
            color: 'var(--text-secondary)',
            padding: '0.25rem 0.5rem',
            background: 'var(--bg-tertiary)',
            borderRadius: '4px'
          }}>
            {displayCameras.length} cameras
          </span>
        </div>
      </div>
      <div className="card-body">
        <div className="camera-grid">
          {displayCameras.map((camera) => (
            <CameraFeed 
              key={camera.id} 
              camera={camera} 
              detectionData={detections[camera.id]}
              videoUrl={camera.url}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

function CameraFeed({ camera, videoUrl }) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [detections, setDetections] = useState([]);
  const [safetyCheck, setSafetyCheck] = useState({
    people_count: 0,
    violation_count: 0,
    compliance_rate: 100
  });
  const [processingTime, setProcessingTime] = useState(0);
  const { confidenceThreshold, updateMetrics, addAlert } = useStore();
  
  const detectFrame = useCallback(async () => {
    const video = videoRef.current;
    const canvas = document.createElement('canvas');
    
    if (!video || video.paused || video.ended) return;
    
    canvas.width = 640;
    canvas.height = 360;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    try {
      const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/jpeg', 0.8));
      const formData = new FormData();
      formData.append('file', blob, 'frame.jpg');
      
      const response = await fetch(`${AI_API_URL}/detect?confidence=${confidenceThreshold}`, {
        method: 'POST',
        body: formData
      });
      
      if (response.ok) {
        const result = await response.json();
        setDetections(result.detections || []);
        setSafetyCheck(result.safety_check || {
          people_count: 0,
          violation_count: 0,
          compliance_rate: 100
        });
        setProcessingTime(result.processing_time_ms || 0);
        
        updateMetrics({
          latency: result.processing_time_ms || 0,
          peopleCount: result.safety_check?.people_count || 0,
          violationCount: result.safety_check?.violation_count || 0,
          complianceRate: result.safety_check?.compliance_rate || 100
        });
        
        if (result.safety_check?.has_violations) {
          result.safety_check.violations?.forEach(v => {
            addAlert({
              id: Date.now() + Math.random(),
              type: 'danger',
              title: v,
              cameraId: camera.id,
              timestamp: Date.now()
            });
          });
        }
      }
    } catch (e) {}
  }, [confidenceThreshold, camera.id, updateMetrics, addAlert]);
  
  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;
    
    video.muted = true;
    video.loop = true;
    video.playsInline = true;
    
    const playVideo = async () => {
      try {
        await video.play();
        setIsPlaying(true);
      } catch (e) {
        console.log('Video autoplay blocked:', e);
      }
    };
    
    video.addEventListener('loadeddata', playVideo);
    
    return () => {
      video.removeEventListener('loadeddata', playVideo);
    };
  }, [videoUrl]);
  
  useEffect(() => {
    if (!isPlaying) return;
    
    const interval = setInterval(detectFrame, 500);
    
    return () => clearInterval(interval);
  }, [isPlaying, detectFrame]);
  
  useEffect(() => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas) return;
    
    const ctx = canvas.getContext('2d');
    let animationId;
    
    const drawFrame = () => {
      if (video.paused || video.ended) {
        animationId = requestAnimationFrame(drawFrame);
        return;
      }
      
      canvas.width = video.videoWidth || 640;
      canvas.height = video.videoHeight || 360;
      
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      
      const scaleX = canvas.width / 640;
      const scaleY = canvas.height / 360;
      
      detections.forEach(det => {
        const [x1, y1, x2, y2] = det.bbox;
        const sx1 = x1 * scaleX;
        const sy1 = y1 * scaleY;
        const sx2 = x2 * scaleX;
        const sy2 = y2 * scaleY;
        
        const isViolation = det.class_name.startsWith('NO-');
        
        ctx.strokeStyle = isViolation ? '#f85149' : '#3fb950';
        ctx.lineWidth = 2;
        ctx.strokeRect(sx1, sy1, sx2 - sx1, sy2 - sy1);
        
        ctx.fillStyle = isViolation ? '#f85149' : '#3fb950';
        const label = `${det.class_name} ${(det.confidence * 100).toFixed(0)}%`;
        ctx.font = '12px Inter, sans-serif';
        const textWidth = ctx.measureText(label).width + 10;
        ctx.fillRect(sx1, sy1 - 20, textWidth, 20);
        
        ctx.fillStyle = '#fff';
        ctx.fillText(label, sx1 + 5, sy1 - 6);
      });
      
      ctx.fillStyle = 'rgba(0,0,0,0.6)';
      ctx.fillRect(canvas.width - 70, 8, 62, 22);
      ctx.fillStyle = '#3fb950';
      ctx.font = '11px JetBrains Mono, monospace';
      ctx.fillText(`${processingTime.toFixed(0)}ms`, canvas.width - 65, 23);
      
      animationId = requestAnimationFrame(drawFrame);
    };
    
    drawFrame();
    
    return () => {
      if (animationId) cancelAnimationFrame(animationId);
    };
  }, [detections, processingTime]);
  
  return (
    <div className="camera-feed" onClick={() => videoRef.current?.play()}>
      <video 
        ref={videoRef}
        src={videoUrl}
        style={{ display: 'none' }}
        crossOrigin="anonymous"
      />
      <canvas 
        ref={canvasRef} 
        style={{ 
          width: '100%', 
          height: '100%', 
          objectFit: 'cover',
          background: '#1a2230'
        }} 
      />
      
      <div className="camera-overlay">
        <div className="camera-header">
          <span className="camera-name">{camera.name}</span>
          <div className="camera-status">
            <span className="live-badge">LIVE</span>
          </div>
        </div>
        
        <div className="camera-stats">
          <div className="stat-item">
            <span className="stat-label">People</span>
            <span className="stat-value">{safetyCheck.people_count}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Violations</span>
            <span className={`stat-value ${safetyCheck.violation_count > 0 ? 'danger' : 'safe'}`}>
              {safetyCheck.violation_count}
            </span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Compliance</span>
            <span className={`stat-value ${safetyCheck.compliance_rate >= 90 ? 'safe' : safetyCheck.compliance_rate >= 70 ? 'warning' : 'danger'}`}>
              {safetyCheck.compliance_rate}%
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
