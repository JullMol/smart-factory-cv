import { useState, useEffect, useCallback } from 'react';

export function useWebSocket(url = 'ws://localhost:8080/ws') {
  const [detections, setDetections] = useState([]);
  const [safetyCheck, setSafetyCheck] = useState(null);
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState(null);
  const [ws, setWs] = useState(null);

  useEffect(() => {
    let websocket;
    let reconnectTimeout;

    const connect = () => {
      try {
        websocket = new WebSocket(url);

        websocket.onopen = () => {
          console.log('WebSocket connected');
          setConnected(true);
          setError(null);
        };

        websocket.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            
            if (data.detections) {
              setDetections(data.detections);
            }
            
            if (data.safety_check) {
              setSafetyCheck(data.safety_check);
            }
          } catch (err) {
            console.error('Failed to parse message:', err);
          }
        };

        websocket.onerror = (err) => {
          console.error('WebSocket error:', err);
          setError('Connection error');
        };

        websocket.onclose = () => {
          console.log('WebSocket disconnected');
          setConnected(false);
          
          reconnectTimeout = setTimeout(() => {
            console.log('Attempting to reconnect...');
            connect();
          }, 3000);
        };

        setWs(websocket);
      } catch (err) {
        console.error('Failed to create WebSocket:', err);
        setError('Failed to connect');
      }
    };

    connect();

    return () => {
      if (reconnectTimeout) {
        clearTimeout(reconnectTimeout);
      }
      if (websocket) {
        websocket.close();
      }
    };
  }, [url]);

  const sendMessage = useCallback((message) => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(message));
    }
  }, [ws]);

  return {
    detections,
    safetyCheck,
    connected,
    error,
    sendMessage
  };
}
