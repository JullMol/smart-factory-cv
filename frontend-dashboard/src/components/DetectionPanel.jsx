import React from 'react';

export function DetectionPanel({ detections = [], safetyCheck = null }) {
  return (
    <div className="detection-panel">
      <h2>Safety Monitor</h2>

      {safetyCheck && (
        <div className={`safety-status ${safetyCheck.has_violations ? 'danger' : 'safe'}`}>
          <div className="status-icon">
            {safetyCheck.has_violations ? 'WARNING' : 'SAFE'}
          </div>
          <div className="status-text">
            {safetyCheck.has_violations ? 'VIOLATION DETECTED' : 'ALL CLEAR'}
          </div>
        </div>
      )}

      {safetyCheck && (
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-value">{safetyCheck.people_count}</div>
            <div className="stat-label">People Detected</div>
          </div>
          
          <div className="stat-card">
            <div className="stat-value">{safetyCheck.violation_count}</div>
            <div className="stat-label">Violations</div>
          </div>
          
          <div className="stat-card">
            <div className="stat-value">{safetyCheck.compliant_count}</div>
            <div className="stat-label">Compliant</div>
          </div>
        </div>
      )}

      {safetyCheck && safetyCheck.violations.length > 0 && (
        <div className="violations-list">
          <h3>Active Violations</h3>
          <ul>
            {safetyCheck.violations.map((violation, idx) => (
              <li key={idx} className="violation-item">
                {violation}
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="detections-list">
        <h3>Detections ({detections.length})</h3>
        <div className="detection-items">
          {detections.length === 0 ? (
            <p className="no-detections">No objects detected</p>
          ) : (
            detections.map((det, idx) => (
              <div key={idx} className="detection-item">
                <span className="detection-class">{det.class_name}</span>
                <span className="detection-confidence">
                  {(det.confidence * 100).toFixed(1)}%
                </span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
