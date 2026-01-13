import React, { useState } from 'react';
import { useWebSocket } from './hooks/useWebSocket';
import { VideoPlayer } from './components/VideoPlayer';
import { DetectionPanel } from './components/DetectionPanel';
import { ImageUpload } from './components/ImageUpload';
import { WebcamDetection } from './components/WebcamDetection';
import './index.css';

function App() {
  const { detections, safetyCheck, connected, error } = useWebSocket();
  const [activeTab, setActiveTab] = useState('webcam');
  const [uploadResult, setUploadResult] = useState(null);

  const handleDetectionResult = (result) => {
    setUploadResult(result);
  };

  return (
    <div className="app">
      <div className="hero-bg"></div>
      
      <header className="app-header">
        <div className="header-content">
          <div className="brand">
            <div className="brand-icon-wrapper">
              <div className="brand-icon">SF</div>
              <div className="icon-glow"></div>
            </div>
            <div className="brand-text">
              <h1>Smart Factory CV</h1>
              <p>AI-Powered Safety Monitoring</p>
            </div>
          </div>
          
          <div className="header-actions">
            <div className="model-badge">
              <span className="badge-label">YOLOv8n</span>
              <span className="badge-value">71.7% mAP</span>
            </div>
            <div className={`connection-badge ${connected ? 'connected' : 'disconnected'}`}>
              <span className="status-pulse"></span>
              <span>{connected ? 'Connected' : 'Offline'}</span>
            </div>
          </div>
        </div>
      </header>

      {error && (
        <div className="error-banner animate-slide-down">
          <span className="error-icon">!</span>
          <span>{error}</span>
          <button className="error-close">X</button>
        </div>
      )}

      <div className="tab-navigation">
        <div className="tab-slider" style={{
          transform: `translateX(${activeTab === 'live' ? '0%' : activeTab === 'webcam' ? '100%' : '200%'})`
        }}></div>
        
        <button 
          className={`tab-button ${activeTab === 'live' ? 'active' : ''}`}
          onClick={() => setActiveTab('live')}
        >
          <span className="tab-label">RTSP Stream</span>
        </button>
        
        <button 
          className={`tab-button ${activeTab === 'webcam' ? 'active' : ''}`}
          onClick={() => setActiveTab('webcam')}
        >
          <span className="tab-label">Webcam</span>
        </button>
        
        <button 
          className={`tab-button ${activeTab === 'upload' ? 'active' : ''}`}
          onClick={() => setActiveTab('upload')}
        >
          <span className="tab-label">Upload</span>
        </button>
      </div>

      <main className="app-main">
        <div className="content-section">
          <div className="section-card animate-fade-in">
            {activeTab === 'live' && (
              <div className="tab-content">
                <VideoPlayer detections={detections} width={640} height={480} />
              </div>
            )}
            
            {activeTab === 'webcam' && (
              <div className="tab-content">
                <WebcamDetection />
              </div>
            )}
            
            {activeTab === 'upload' && (
              <div className="tab-content">
                <ImageUpload onDetectionResult={handleDetectionResult} />
              </div>
            )}
          </div>
        </div>
        
        <div className="sidebar-section">
          <div className="section-card animate-fade-in-delay">
            <DetectionPanel 
              detections={activeTab === 'upload' ? (uploadResult?.detections || []) : detections} 
              safetyCheck={activeTab === 'upload' ? (uploadResult?.safety_check || null) : safetyCheck} 
            />
          </div>
        </div>
      </main>

      <footer className="app-footer">
        <div className="footer-content">
          <div className="footer-left">
            <span className="footer-brand">Smart Factory CV</span>
            <span className="footer-divider">|</span>
            <span>Powered by YOLOv8 + RTX 4050</span>
          </div>
          <div className="footer-right">
            <div className="footer-stat">
              <span className="stat-label">Model</span>
              <span className="stat-value">6.3MB</span>
            </div>
            <div className="footer-stat">
              <span className="stat-label">Speed</span>
              <span className="stat-value">2.1ms</span>
            </div>
            <div className="footer-stat">
              <span className="stat-label">Accuracy</span>
              <span className="stat-value">71.7%</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
