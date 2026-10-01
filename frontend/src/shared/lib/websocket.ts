type EventHandler = (payload: any) => void;

export class WebSocketClient {
  private url: string;
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private isConnecting = false;
  private handlers = new Map<string, Set<EventHandler>>();
  private tokenProvider: () => string | null;
  
  constructor(url: string, tokenProvider: () => string | null) {
    this.url = url;
    this.tokenProvider = tokenProvider;
  }

  connect() {
    if (this.ws?.readyState === WebSocket.OPEN || this.isConnecting) return;
    
    this.isConnecting = true;
    const token = this.tokenProvider();
    
    // Pass token as query param (backend would need to parse this or we rely on session cookies)
    const wsUrl = token ? `${this.url}?token=${token}` : this.url;
    
    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      console.log('[WebSocket] Connected');
      this.isConnecting = false;
      this.reconnectAttempts = 0;
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type) {
          this.emit(data.type, data.payload);
        }
      } catch (err) {
        console.error('[WebSocket] Message parse error:', err);
      }
    };

    this.ws.onclose = () => {
      console.log('[WebSocket] Disconnected');
      this.isConnecting = false;
      this.ws = null;
      this.attemptReconnect();
    };

    this.ws.onerror = (err) => {
      console.error('[WebSocket] Error:', err);
    };
  }

  private attemptReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.warn('[WebSocket] Max reconnect attempts reached');
      return;
    }

    this.reconnectAttempts++;
    const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 10000);
    const jitter = Math.random() * 1000;
    
    setTimeout(() => this.connect(), delay + jitter);
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  subscribe(type: string, handler: EventHandler) {
    if (!this.handlers.has(type)) {
      this.handlers.set(type, new Set());
    }
    this.handlers.get(type)!.add(handler);
    
    return () => this.unsubscribe(type, handler);
  }

  unsubscribe(type: string, handler: EventHandler) {
    const handlers = this.handlers.get(type);
    if (handlers) {
      handlers.delete(handler);
    }
  }

  private emit(type: string, payload: any) {
    const handlers = this.handlers.get(type);
    if (handlers) {
      handlers.forEach(handler => handler(payload));
    }
  }
}

export const wsClient = new WebSocketClient(
  'ws://localhost:8000/ws/notifications/',
  () => localStorage.getItem('access_token')
);
