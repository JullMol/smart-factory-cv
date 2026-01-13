import React, { useRef, useState, useEffect } from 'react';

export function WebcamDetection() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [isActive, setIsActive] = useState(false);
  const [detections, setDetections] = useState([]);
  const [fps, setFps] = useState(0);
  const [processing, setProcessing] = useState(false);
  const intervalRef = useRef(null);

  useEffect(() => {
    return () => {
      stopWebcam();
    };
  }, []);

  const startWebcam = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 480 }
      });
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        setIsActive(true);
        startDetection();
      }
    } catch (error) {
      console.error('Error accessing webcam:', error);
      alert('Cannot access webcam. Please check permissions.');
    }
  };

  const stopWebcam = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const tracks = videoRef.current.srcObject.getTracks();
      tracks.forEach(track => track.stop());
      videoRef.current.srcObject = null;
    }
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }
    setIsActive(false);
    setDetections([]);
  };

  const startDetection = () => {
    let frameCount = 0;
    let lastTime = Date.now();

    intervalRef.current = setInterval(async () => {
      if (!videoRef.current || processing) return;

      const canvas = document.createElement('canvas');
      canvas.width = 640;
      canvas.height = 480;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(videoRef.current, 0, 0, 640, 480);

      canvas.toBlob(async (blob) => {
        if (!blob) return;

        setProcessing(true);
        const formData = new FormData();
        formData.append('file', blob, 'frame.jpg');

        try {
          const response = await fetch('http://localhost:8000/detect', {
            method: 'POST',
            body: formData,
          });

          if (response.ok) {
            const data = await response.json();
            setDetections(data.detections || []);
            drawDetections(data.detections || []);
          }
        } catch (error) {
          console.error('Detection error:', error);
        } finally {
          setProcessing(false);
        }

        frameCount++;
        const now = Date.now();
        if (now - lastTime >= 1000) {
          setFps(frameCount);
          frameCount = 0;
          lastTime = now;
        }
      }, 'image/jpeg', 0.8);
    }, 500);
  };

  const drawDetections = (dets) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const CLASS_COLORS = {
      0: '#00FF00', 1: '#FF00FF', 2: '#FF4500', 3: '#FFA500',
      4: '#FFA500', 5: '#00FFFF', 6: '#FFFF00', 7: '#00FF00',
      8: '#808080', 9: '#0000FF',
    };

    dets.forEach(det => {
      const [x1, y1, x2, y2] = det.bbox;
      const color = CLASS_COLORS[det.class_id] || '#FFFFFF';

      ctx.strokeStyle = color;
      ctx.lineWidth = 3;
      ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);

      ctx.shadowColor = color;
      ctx.shadowBlur = 15;

      const label = `${det.class_name} ${(det.confidence * 100).toFixed(0)}%`;
      ctx.font = 'bold 16px Inter';
      const metrics = ctx.measureText(label);

      ctx.fillStyle = color;
      ctx.fillRect(x1, y1 - 28, metrics.width + 12, 28);

      ctx.shadowBlur = 0;
      ctx.fillStyle = '#000';
      ctx.fillText(label, x1 + 6, y1 - 8);
    });
  };

  return (
    <div className="webcam-container">
      <div className="webcam-controls">
        {!isActive ? (
          <button onClick={startWebcam} className="btn-webcam btn-start">
            <span>Start Webcam</span>
          </button>
        ) : (
          <button onClick={stopWebcam} className="btn-webcam btn-stop">
            <span>Stop Webcam</span>
          </button>
        )}
      </div>

      <div className="webcam-display">
        <div className="video-wrapper">
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            width={640}
            height={480}
            className="webcam-video"
          />
          <canvas
            ref={canvasRef}
            width={640}
            height={480}
            className="detection-canvas"
          />
          
          {isActive && (
            <div className="webcam-stats">
              <div className="stat-badge">
                <span>{fps} FPS</span>
              </div>
              <div className="stat-badge">
                <span>{detections.length} Objects</span>
              </div>
            </div>
          )}
        </div>

        {!isActive && (
          <div className="webcam-placeholder">
            <p>Click "Start Webcam" to begin real-time detection</p>
          </div>
        )}
      </div>
    </div>
  );
}
