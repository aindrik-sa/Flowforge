import React, { useState, useEffect } from 'react';
import { wsClient } from '@/shared/lib/websocket';
import './ConnectionStatus.css';

export function ConnectionStatus() {
  const [status, setStatus] = useState<'connected' | 'reconnecting' | 'offline'>('offline');

  useEffect(() => {
    // Basic polling or event hook into wsClient could be here
    // For now we'll just simulate it reading from our global instance
    const interval = setInterval(() => {
      // @ts-ignore - access private properties for demo
      if (wsClient.ws?.readyState === WebSocket.OPEN) {
        setStatus('connected');
      // @ts-ignore
      } else if (wsClient.isConnecting) {
        setStatus('reconnecting');
      } else {
        setStatus('offline');
      }
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  const getTooltip = () => {
    if (status === 'connected') return 'Real-time Sync Active';
    if (status === 'reconnecting') return 'Reconnecting...';
    return 'Offline. Sync paused.';
  };

  return (
    <div className="connection-status" title={getTooltip()}>
      <div className={`status-dot status-${status}`}></div>
      <span className="status-text capitalize">{status}</span>
    </div>
  );
}
