import { create } from 'zustand';

const useStore = create((set, get) => ({
  cameras: [],
  zones: [], 
  detections: {},
  alerts: [],
  metrics: {
    latency: 0,
    peopleCount: 0,
    violationCount: 0,
    complianceRate: 100
  },
  isConnected: false, 
  confidenceThreshold: 0.5,
  
  setConnected: (status) => set({ isConnected: status }),
  setCameras: (cameras) => set({ cameras }),
  
  updateDetections: (cameraId, data) => set((state) => ({
    detections: { ...state.detections, [cameraId]: data }
  })),
  
  addAlert: (alert) => set((state) => ({
    alerts: [alert, ...state.alerts].slice(0, 10)
  })),
  
  clearAlerts: () => set({ alerts: [] }),
  
  updateMetrics: (metrics) => set((state) => ({
    metrics: { ...state.metrics, ...metrics }
  })),
  
  setConfidenceThreshold: (threshold) => set({ confidenceThreshold: threshold })
}));

export default useStore;
