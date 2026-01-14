import React, { useEffect } from 'react';
import useStore from './store/store';
import Header from './components/layout/Header';
import CameraGrid from './components/monitoring/CameraGrid';

export default function App() {
  const { isConnected, setConnected, metrics, alerts, clearAlerts, confidenceThreshold, setConfidenceThreshold } = useStore();
  const AI_API_URL = import.meta.env.VITE_AI_API_URL || 'http://localhost:8000';

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await fetch(`${AI_API_URL}/health`);
        setConnected(res.ok);
      } catch (e) {
        setConnected(false);
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 5000);
    return () => clearInterval(interval);
  }, [setConnected]);

  const formatTime = (timestamp) => {
    const diff = Date.now() - timestamp;
    if (diff < 60000) return 'Just now';
    return `${Math.floor(diff / 60000)}m ago`;
  };

  return (
    <div className="app">
      <div className="hero-bg" />
      <Header connected={isConnected} />
      
      <main className="main-layout">
        {/* Left: Metrics Panel */}
        <aside className="metrics-sidebar">
          <div className="metrics-compact">
            <div className="metric-item">
              <span className="metric-val" style={{ color: 'var(--accent-blue)' }}>
                {metrics.latency.toFixed(0)}
              </span>
              <span className="metric-lbl">ms</span>
            </div>
            <div className="metric-item">
              <span className="metric-val" style={{ color: 'var(--accent-purple)' }}>
                {metrics.peopleCount}
              </span>
              <span className="metric-lbl">People</span>
            </div>
            <div className="metric-item">
              <span className="metric-val" style={{ 
                color: metrics.complianceRate >= 90 ? 'var(--accent-green)' : 
                       metrics.complianceRate >= 70 ? 'var(--accent-yellow)' : 'var(--accent-red)'
              }}>
                {metrics.complianceRate}%
              </span>
              <span className="metric-lbl">Compliance</span>
            </div>
          </div>
          
          <div className="threshold-control">
            <label>Confidence: {(confidenceThreshold * 100).toFixed(0)}%</label>
            <input
              type="range"
              min="0.1"
              max="0.95"
              step="0.05"
              value={confidenceThreshold}
              onChange={(e) => setConfidenceThreshold(parseFloat(e.target.value))}
            />
          </div>
        </aside>
        
        {/* Center: Camera Grid */}
        <section className="camera-section">
          <CameraGrid />
        </section>
        
        {/* Right: Compact Alerts */}
        <aside className="alerts-sidebar">
          <div className="alerts-header">
            <span>Alerts ({alerts.length})</span>
            {alerts.length > 0 && (
              <button onClick={clearAlerts} className="clear-btn">Clear</button>
            )}
          </div>
          <div className="alerts-compact">
            {alerts.length === 0 ? (
              <div className="no-alerts">No violations detected</div>
            ) : (
              alerts.slice(0, 5).map(alert => (
                <div key={alert.id} className="alert-mini">
                  <span className="alert-icon">⚠</span>
                  <div className="alert-info">
                    <span className="alert-text">{alert.title}</span>
                    <span className="alert-time">{alert.cameraId} • {formatTime(alert.timestamp)}</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </aside>
      </main>
    </div>
  );
}
