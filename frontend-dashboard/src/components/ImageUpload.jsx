import React, { useState } from 'react';

export function ImageUpload({ onDetectionResult }) {
  const [selectedImage, setSelectedImage] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleImageSelect = (e) => {
    const file = e.target.files[0];
    if (file && file.type.startsWith('image/')) {
      setSelectedImage(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result);
      };
      reader.readAsDataURL(file);
      setResult(null);
    }
  };

  const handleUpload = async () => {
    if (!selectedImage) return;

    setLoading(true);
    const formData = new FormData();
    formData.append('file', selectedImage);

    try {
      const response = await fetch('http://localhost:8000/detect', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        setResult(data);
        if (onDetectionResult) {
          onDetectionResult(data);
        }
      } else {
        console.error('Detection failed:', response.statusText);
      }
    } catch (error) {
      console.error('Error uploading image:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setSelectedImage(null);
    setPreview(null);
    setResult(null);
  };

  return (
    <div className="image-upload-container">
      <div className="upload-section">
        <input
          type="file"
          accept="image/*"
          onChange={handleImageSelect}
          id="image-input"
          style={{ display: 'none' }}
        />
        
        <label htmlFor="image-input" className="upload-button">
          <span>Choose Image</span>
        </label>

        {selectedImage && (
          <div className="upload-actions">
            <button 
              onClick={handleUpload} 
              disabled={loading}
              className="btn btn-primary"
            >
              {loading ? 'Processing...' : 'Detect PPE'}
            </button>
            <button onClick={handleClear} className="btn btn-secondary">
              Clear
            </button>
          </div>
        )}
      </div>

      {preview && (
        <div className="preview-section">
          <div className="image-preview">
            <img src={preview} alt="Preview" />
            {result && result.detections && (
              <canvas
                className="detection-overlay"
                ref={(canvas) => {
                  if (canvas && result) {
                    drawDetections(canvas, result.detections);
                  }
                }}
              />
            )}
          </div>
        </div>
      )}

      {result && (
        <div className="result-summary">
          <div className="result-header">
            <h3>Detection Results</h3>
            <span className="processing-time">
              {result.processing_time_ms.toFixed(1)}ms
            </span>
          </div>
          
          <div className="detection-stats">
            <div className="stat">
              <span className="stat-value">{result.detections.length}</span>
              <span className="stat-label">Objects</span>
            </div>
            <div className="stat">
              <span className="stat-value">{result.safety_check.people_count}</span>
              <span className="stat-label">People</span>
            </div>
            <div className="stat">
              <span className="stat-value">{result.safety_check.violation_count}</span>
              <span className="stat-label">Violations</span>
            </div>
          </div>

          {result.safety_check.violations.length > 0 && (
            <div className="violations-alert">
              <strong>Safety Violations:</strong>
              <ul>
                {result.safety_check.violations.map((v, i) => (
                  <li key={i}>{v}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function drawDetections(canvas, detections) {
  const ctx = canvas.getContext('2d');
  const img = canvas.previousSibling;
  
  canvas.width = img.width;
  canvas.height = img.height;

  const CLASS_COLORS = {
    0: '#00FF00', 1: '#FF00FF', 2: '#FF4500', 3: '#FFA500',
    4: '#FFA500', 5: '#00FFFF', 6: '#FFFF00', 7: '#00FF00',
    8: '#808080', 9: '#0000FF',
  };

  detections.forEach(det => {
    const [x1, y1, x2, y2] = det.bbox;
    const color = CLASS_COLORS[det.class_id] || '#FFFFFF';

    ctx.strokeStyle = color;
    ctx.lineWidth = 3;
    ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);

    const label = `${det.class_name} ${(det.confidence * 100).toFixed(0)}%`;
    ctx.font = '16px Arial';
    const metrics = ctx.measureText(label);

    ctx.fillStyle = color;
    ctx.fillRect(x1, y1 - 25, metrics.width + 10, 25);

    ctx.fillStyle = '#000';
    ctx.fillText(label, x1 + 5, y1 - 7);
  });
}
