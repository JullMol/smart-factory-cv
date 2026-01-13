import React from 'react';
import { motion } from 'framer-motion';
import useStore from '../../store/store';

const CAMERA_POSITIONS = [
  { id: 'cam-1', name: 'Main Entrance', x: 15, y: 20, zone: 'Entry' },
  { id: 'cam-2', name: 'Assembly Line A', x: 45, y: 35, zone: 'Production' },
  { id: 'cam-3', name: 'Loading Dock', x: 80, y: 25, zone: 'Shipping' },
  { id: 'cam-4', name: 'Machine Shop', x: 55, y: 70, zone: 'Manufacturing' }
];

const ZONES = [
  { id: 'z1', name: 'Entry Zone', x: 5, y: 10, width: 25, height: 30, color: '#3fb950' },
  { id: 'z2', name: 'Production Floor', x: 32, y: 20, width: 35, height: 35, color: '#58a6ff' },
  { id: 'z3', name: 'Shipping Area', x: 70, y: 10, width: 25, height: 40, color: '#d29922' },
  { id: 'z4', name: 'Manufacturing', x: 40, y: 58, width: 40, height: 35, color: '#a371f7' }
];

export default function FloorPlan() {
  const { alerts, zones: storeZones } = useStore();
  
  const activeViolations = alerts.filter(a => 
    Date.now() - a.timestamp < 30000 && a.type === 'danger'
  );
  
  const getCameraStatus = (camId) => {
    const hasViolation = activeViolations.some(v => v.cameraId === camId);
    return hasViolation ? 'violation' : 'normal';
  };
  
  return (
    <div className="card">
      <div className="card-header">
        <span className="card-title">Factory Floor Plan</span>
        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          <span style={{ 
            width: 8, height: 8, borderRadius: '50%', 
            background: '#3fb950', display: 'inline-block' 
          }}></span>
          <span style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>Safe</span>
          <span style={{ 
            width: 8, height: 8, borderRadius: '50%', 
            background: '#f85149', display: 'inline-block', marginLeft: '0.5rem'
          }}></span>
          <span style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>Violation</span>
        </div>
      </div>
      <div className="card-body" style={{ padding: '0.5rem' }}>
        <div style={{
          position: 'relative',
          width: '100%',
          aspectRatio: '16/10',
          background: 'linear-gradient(135deg, #0d1117 0%, #161b22 100%)',
          borderRadius: 'var(--radius-md)',
          overflow: 'hidden',
          border: '1px solid var(--border-default)'
        }}>
          <svg width="100%" height="100%" viewBox="0 0 100 100" preserveAspectRatio="xMidYMid meet">
            <defs>
              <pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse">
                <path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(48,54,61,0.5)" strokeWidth="0.2"/>
              </pattern>
              <filter id="glow">
                <feGaussianBlur stdDeviation="1.5" result="coloredBlur"/>
                <feMerge>
                  <feMergeNode in="coloredBlur"/>
                  <feMergeNode in="SourceGraphic"/>
                </feMerge>
              </filter>
            </defs>
            
            <rect width="100" height="100" fill="url(#grid)"/>
            
            {ZONES.map(zone => (
              <g key={zone.id}>
                <rect
                  x={zone.x}
                  y={zone.y}
                  width={zone.width}
                  height={zone.height}
                  fill={zone.color}
                  fillOpacity={0.1}
                  stroke={zone.color}
                  strokeWidth={0.3}
                  strokeDasharray="2,1"
                  rx={1}
                />
                <text
                  x={zone.x + zone.width/2}
                  y={zone.y + 3}
                  textAnchor="middle"
                  fill={zone.color}
                  fontSize={2.5}
                  fontFamily="Inter, sans-serif"
                  opacity={0.7}
                >
                  {zone.name}
                </text>
              </g>
            ))}
            
            <rect x={1} y={1} width={98} height={98} 
              fill="none" stroke="#30363d" strokeWidth={0.5} rx={2}/>
            
            <line x1={30} y1={1} x2={30} y2={55} stroke="#30363d" strokeWidth={0.3}/>
            <line x1={68} y1={1} x2={68} y2={55} stroke="#30363d" strokeWidth={0.3}/>
            <line x1={1} y1={55} x2={99} y2={55} stroke="#30363d" strokeWidth={0.3}/>
            
            {CAMERA_POSITIONS.map(cam => {
              const status = getCameraStatus(cam.id);
              const isViolation = status === 'violation';
              
              return (
                <g key={cam.id} style={{ cursor: 'pointer' }}>
                  {isViolation && (
                    <circle
                      cx={cam.x}
                      cy={cam.y}
                      r={6}
                      fill="#f85149"
                      opacity={0.3}
                      filter="url(#glow)"
                    >
                      <animate
                        attributeName="r"
                        values="4;8;4"
                        dur="1.5s"
                        repeatCount="indefinite"
                      />
                      <animate
                        attributeName="opacity"
                        values="0.5;0.1;0.5"
                        dur="1.5s"
                        repeatCount="indefinite"
                      />
                    </circle>
                  )}
                  
                  <circle
                    cx={cam.x}
                    cy={cam.y}
                    r={isViolation ? 3 : 2.5}
                    fill={isViolation ? '#f85149' : '#3fb950'}
                    stroke="#0d1117"
                    strokeWidth={0.5}
                    filter="url(#glow)"
                  />
                  
                  <text
                    x={cam.x}
                    y={cam.y + 6}
                    textAnchor="middle"
                    fill="#8b949e"
                    fontSize={2}
                    fontFamily="Inter, sans-serif"
                  >
                    {cam.name}
                  </text>
                </g>
              );
            })}
            
            <rect x={2} y={85} width={15} height={12} fill="#161b22" stroke="#30363d" strokeWidth={0.3} rx={1}/>
            <text x={9.5} y={90} textAnchor="middle" fill="#8b949e" fontSize={2}>Control</text>
            <text x={9.5} y={93} textAnchor="middle" fill="#8b949e" fontSize={2}>Room</text>
            
            <rect x={83} y={85} width={14} height={12} fill="#161b22" stroke="#30363d" strokeWidth={0.3} rx={1}/>
            <text x={90} y={92} textAnchor="middle" fill="#8b949e" fontSize={2}>Storage</text>
          </svg>
        </div>
      </div>
    </div>
  );
}
