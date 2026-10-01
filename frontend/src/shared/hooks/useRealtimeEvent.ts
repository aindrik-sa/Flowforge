import { useEffect } from 'react';
import { wsClient } from '../lib/websocket';

export function useRealtimeEvent<T = any>(type: string, handler: (payload: T) => void) {
  useEffect(() => {
    // Only connect if we have an active hook
    wsClient.connect();
    
    const unsubscribe = wsClient.subscribe(type, handler);
    return () => {
      unsubscribe();
    };
  }, [type, handler]);
}
