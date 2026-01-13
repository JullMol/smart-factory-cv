import React from 'react';
import { useWebSocket } from './hooks/useWebSocket';
import useStore from './store/store';
import Header from './components/layout/Header';
import Sidebar from './components/layout/Sidebar';
import CameraGrid from './components/monitoring/CameraGrid';
import AlertPanel from './components/alerts/AlertPanel';
import './styles/index.css';

function App() {
  useWebSocket();
  const { connected } = useStore();
  
  return (
    <div className="app">
      <div className="hero-bg"></div>
      
      <Header connected={connected} />
      
      <main className="main">
        <Sidebar />
        
        <div className="content">
          <CameraGrid />
        </div>
        
        <div className="alerts-panel">
          <AlertPanel />
        </div>
      </main>
    </div>
  );
}

export default App;
