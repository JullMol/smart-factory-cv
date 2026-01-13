import { create } from 'zustand';

const useStore = create((set, get) => ({
  connected: false,
  cameras: [],
  detections: {},
  alerts: [],
  metrics: {
    fps: 0,
    latency: 0,
    peopleCount: 0,
    violationCount: 0,
    complianceRate: 100
  },
  zones: [],
  confidenceThreshold: 0.5,
  
  setConnected: (connected) => set({ connected }),
  
  addCamera: (camera) => set((state) => ({
    cameras: [...state.cameras.filter(c => c.id !== camera.id), camera]
  })),
  
  removeCamera: (cameraId) => set((state) => ({
    cameras: state.cameras.filter(c => c.id !== cameraId)
  })),
  
  updateDetections: (cameraId, data) => set((state) => ({
    detections: { ...state.detections, [cameraId]: data }
  })),
  
  addAlert: (alert) => set((state) => ({
    alerts: [alert, ...state.alerts].slice(0, 100)
  })),
  
  clearAlerts: () => set({ alerts: [] }),
  
  updateMetrics: (metrics) => set((state) => ({
    metrics: { ...state.metrics, ...metrics }
  })),
  
  setZones: (zones) => set({ zones }),
  
  setConfidenceThreshold: (threshold) => set({ confidenceThreshold: threshold }),
  
  processMessage: (message) => {
    const state = get();
    
    switch (message.type) {
      case 'detection':
        state.updateDetections(message.camera_id, message.data);
        
        if (message.data.safety_check) {
          state.updateMetrics({
            peopleCount: message.data.safety_check.people_count,
            violationCount: message.data.safety_check.violation_count,
            complianceRate: message.data.safety_check.compliance_rate,
            latency: message.data.processing_time_ms
          });
          
          if (message.data.safety_check.has_violations) {
            message.data.safety_check.violations.forEach(violation => {
              state.addAlert({
                id: Date.now() + Math.random(),
                type: 'warning',
                title: violation,
                cameraId: message.camera_id,
                timestamp: message.timestamp
              });
            });
          }
        }
        
        if (message.data.zone_violations) {
          message.data.zone_violations.forEach(v => {
            state.addAlert({
              id: Date.now() + Math.random(),
              type: v.severity,
              title: `Zone Violation: ${v.zone_name}`,
              details: v.missing_ppe.join(', '),
              cameraId: message.camera_id,
              timestamp: v.timestamp
            });
          });
        }
        break;
        
      case 'metrics':
        state.updateMetrics(message.data);
        break;
        
      case 'zones':
        state.setZones(message.data);
        break;
    }
  }
}));

export default useStore;
