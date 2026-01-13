import { useEffect, useRef, useCallback } from 'react';
import useStore from '../store/store';

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8080/ws';

export function useWebSocket() {
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const { setConnected, processMessage } = useStore();
  
  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;
    
    try {
      wsRef.current = new WebSocket(WS_URL);
      
      wsRef.current.onopen = () => {
        setConnected(true);
        if (reconnectTimeoutRef.current) {
          clearTimeout(reconnectTimeoutRef.current);
          reconnectTimeoutRef.current = null;
        }
      };
      
      wsRef.current.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          processMessage(message);
        } catch (e) {
          console.error('Failed to parse message:', e);
        }
      };
      
      wsRef.current.onclose = () => {
        setConnected(false);
        reconnectTimeoutRef.current = setTimeout(connect, 3000);
      };
      
      wsRef.current.onerror = () => {
        wsRef.current?.close();
      };
    } catch (e) {
      setConnected(false);
      reconnectTimeoutRef.current = setTimeout(connect, 3000);
    }
  }, [setConnected, processMessage]);
  
  const subscribe = useCallback((cameraIds) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'subscribe',
        cameras: cameraIds
      }));
    }
  }, []);
  
  useEffect(() => {
    connect();
    
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [connect]);
  
  return { subscribe };
}
