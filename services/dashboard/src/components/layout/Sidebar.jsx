import React from 'react';
import useStore from '../../store/store';
import { LineChart, Line, ResponsiveContainer } from 'recharts';

export default function Sidebar() {
  const { metrics, confidenceThreshold, setConfidenceThreshold, zones = [] } = useStore();
  
  const mockHistory = Array.from({ length: 20 }, (_, i) => ({
    time: i,
    rate: 85 + Math.random() * 15
  }));
  
  return (
    <aside className="sidebar">
      <div className="card">
        <div className="card-header">
          <span className="card-title">System Metrics</span>
        </div>
        <div className="card-body">
          <div className="metrics-grid">
            <div className="metric-card">
              <div className="metric-value" style={{ color: 'var(--accent-blue)' }}>
                {metrics.latency.toFixed(1)}
              </div>
              <div className="metric-label">Latency (ms)</div>
            </div>
            <div className="metric-card">
              <div className="metric-value" style={{ color: 'var(--accent-green)' }}>
                {metrics.fps || 15}
              </div>
              <div className="metric-label">FPS</div>
            </div>
            <div className="metric-card">
              <div className="metric-value" style={{ color: 'var(--accent-purple)' }}>
                {metrics.peopleCount}
              </div>
              <div className="metric-label">People</div>
            </div>
            <div className="metric-card">
              <div className="metric-value" style={{ 
                color: metrics.complianceRate >= 90 ? 'var(--accent-green)' : 
                       metrics.complianceRate >= 70 ? 'var(--accent-yellow)' : 'var(--accent-red)'
              }}>
                {metrics.complianceRate}%
              </div>
              <div className="metric-label">Compliance</div>
            </div>
          </div>
        </div>
      </div>
      
      <div className="card">
        <div className="card-header">
          <span className="card-title">Compliance Trend</span>
        </div>
        <div className="card-body">
          <div className="chart-container" style={{ height: 120 }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={mockHistory}>
                <Line 
                  type="monotone" 
                  dataKey="rate" 
                  stroke="var(--accent-green)" 
                  strokeWidth={2}
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
      
      <div className="card">
        <div className="card-header">
          <span className="card-title">Danger Zones</span>
        </div>
        <div className="card-body">
          <div className="zone-list">
            {zones.length === 0 ? (
              <>
                <div className="zone-item">
                  <div className="zone-indicator danger"></div>
                  <span className="zone-name">Machine Area</span>
                  <span className="zone-count">2</span>
                </div>
                <div className="zone-item">
                  <div className="zone-indicator warning"></div>
                  <span className="zone-name">Loading Dock</span>
                  <span className="zone-count">0</span>
                </div>
                <div className="zone-item">
                  <div className="zone-indicator critical"></div>
                  <span className="zone-name">Assembly Line</span>
                  <span className="zone-count">1</span>
                </div>
              </>
            ) : (
              zones.map(zone => (
                <div className="zone-item" key={zone.id}>
                  <div className={`zone-indicator ${zone.severity}`}></div>
                  <span className="zone-name">{zone.name}</span>
                  <span className="zone-count">0</span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
      
      <div className="card">
        <div className="card-header">
          <span className="card-title">Settings</span>
        </div>
        <div className="card-body">
          <div className="slider-container">
            <div className="slider-header">
              <span className="slider-label">Confidence Threshold</span>
              <span className="slider-value">{(confidenceThreshold * 100).toFixed(0)}%</span>
            </div>
            <input
              type="range"
              className="slider"
              min="0.1"
              max="0.95"
              step="0.05"
              value={confidenceThreshold}
              onChange={(e) => setConfidenceThreshold(parseFloat(e.target.value))}
            />
          </div>
        </div>
      </div>
    </aside>
  );
}
