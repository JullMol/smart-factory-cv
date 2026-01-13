import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import useStore from '../../store/store';

export default function AlertPanel() {
  const { alerts, clearAlerts } = useStore();
  
  const formatTime = (timestamp) => {
    const diff = Date.now() - timestamp;
    if (diff < 60000) return 'Just now';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    return `${Math.floor(diff / 3600000)}h ago`;
  };
  
  return (
    <div className="card" style={{ flex: 1, display: 'flex', flexDirection: 'column', maxHeight: 'calc(100vh - 100px)' }}>
      <div className="card-header">
        <span className="card-title">
          Safety Alerts
          {alerts.length > 0 && (
            <span style={{
              marginLeft: '0.5rem',
              padding: '0.1rem 0.4rem',
              background: 'var(--accent-red)',
              borderRadius: '10px',
              fontSize: '0.65rem',
              fontWeight: 700
            }}>
              {alerts.length}
            </span>
          )}
        </span>
        {alerts.length > 0 && (
          <button className="btn btn-ghost" onClick={clearAlerts} style={{ padding: '0.25rem 0.5rem', fontSize: '0.7rem' }}>
            Clear
          </button>
        )}
      </div>
      <div className="card-body" style={{ flex: 1, overflow: 'hidden', padding: '0.5rem' }}>
        <div style={{ 
          height: '100%', 
          overflowY: 'auto',
          display: 'flex',
          flexDirection: 'column',
          gap: '0.5rem',
          paddingRight: '0.5rem'
        }}>
          <AnimatePresence mode="popLayout">
            {alerts.slice(0, 50).map((alert) => (
              <motion.div
                key={alert.id}
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, x: -20 }}
                layout
                className={`alert-card ${alert.type}`}
              >
                <div className="alert-thumbnail">
                  <div style={{
                    width: '100%',
                    height: '100%',
                    background: alert.type === 'danger' 
                      ? 'linear-gradient(135deg, #da3633, #8b2320)' 
                      : alert.type === 'warning'
                      ? 'linear-gradient(135deg, #9e6a03, #6b4701)'
                      : 'linear-gradient(135deg, #8957e5, #5c3d99)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '1rem'
                  }}>
                    {alert.type === 'danger' ? '⚠️' : alert.type === 'warning' ? '⚡' : '🔒'}
                  </div>
                </div>
                <div className="alert-content">
                  <div className="alert-title">{alert.title}</div>
                  {alert.details && (
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', marginBottom: '0.2rem' }}>
                      {alert.details}
                    </div>
                  )}
                  <div className="alert-meta">
                    {alert.cameraId} • {formatTime(alert.timestamp)}
                  </div>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
          
          {alerts.length === 0 && (
            <div style={{
              textAlign: 'center',
              padding: '2rem',
              color: 'var(--text-muted)'
            }}>
              <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>✓</div>
              <div>No active alerts</div>
              <div style={{ fontSize: '0.75rem', marginTop: '0.25rem' }}>All workers are compliant</div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
