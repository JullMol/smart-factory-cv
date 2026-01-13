import React, { useRef, useEffect } from 'react';

export function VideoPlayer({ detections = [], width = 640, height = 480 }) {
  const canvasRef = useRef(null);

  const CLASS_COLORS = {
    0: '#00FF00',
    1: '#FF00FF',
    2: '#FF4500',
    3: '#FFA500',
    4: '#FFA500',
    5: '#00FFFF',
    6: '#FFFF00',
    7: '#00FF00',
    8: '#808080',
    9: '#0000FF',
  };

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    detections.forEach(det => {
      const [x1, y1, x2, y2] = det.bbox;
      const color = CLASS_COLORS[det.class_id] || '#FFFFFF';

      ctx.strokeStyle = color;
      ctx.lineWidth = 3;
      ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);

      const label = `${det.class_name} ${(det.confidence * 100).toFixed(0)}%`;
      ctx.font = '16px Arial';
      const metrics = ctx.measureText(label);
      const labelHeight = 20;

      ctx.fillStyle = color;
      ctx.fillRect(x1, y1 - labelHeight - 2, metrics.width + 10, labelHeight + 2);

      ctx.fillStyle = '#000000';
      ctx.fillText(label, x1 + 5, y1 - 5);
    });
  }, [detections]);

  return (
    <div className="video-player">
      <div className="video-container" style={{ position: 'relative', width, height }}>
        <div 
          className="placeholder-video"
          style={{
            width: '100%',
            height: '100%',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
            fontSize: '24px'
          }}
        >
          Live Stream
        </div>
        
        <canvas
          ref={canvasRef}
          width={width}
          height={height}
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            pointerEvents: 'none'
          }}
        />
      </div>

      <div className="video-info">
        <span>Detections: {detections.length}</span>
      </div>
    </div>
  );
}
