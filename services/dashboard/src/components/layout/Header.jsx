import React from 'react';

export default function Header({ connected }) {
  return (
    <header className="header">
      <div className="header-content">
        <div className="brand">
          <div className="brand-icon">SF</div>
          <div className="brand-text">
            <h1>Smart Factory CV</h1>
            <p>Industrial AI Safety Monitoring</p>
          </div>
        </div>
        
        <div className="header-actions">
          <div className="model-badge">
            <span style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>Model</span>
            <span style={{ fontWeight: 600, marginLeft: '0.25rem' }}>YOLOv8n ONNX</span>
          </div>
          
          <div className={`connection-badge ${connected ? 'connected' : 'disconnected'}`}>
            <span className="status-dot"></span>
            <span>{connected ? 'Connected' : 'Offline'}</span>
          </div>
        </div>
      </div>
    </header>
  );
}
