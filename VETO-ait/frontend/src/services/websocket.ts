type MessageHandler = (type: string, data: any) => void;

class WebSocketClient {
  private ws: WebSocket | null = null;
  private handlers: Set<MessageHandler> = new Set();
  private reconnectInterval = 3000;
  private isConnecting = false;

  public connect() {
    if (this.ws && (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING)) {
      return;
    }
    this.isConnecting = true;
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;

    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      this.isConnecting = false;
      // Broadcast connection event
      this.notifyHandlers('CONNECTED', {});
    };

    this.ws.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        if (payload.type) {
          this.notifyHandlers(payload.type, payload.data);
        }
      } catch (e) {
        // Ignored
      }
    };

    this.ws.onclose = () => {
      this.isConnecting = false;
      this.ws = null;
      this.notifyHandlers('DISCONNECTED', {});
      setTimeout(() => this.connect(), this.reconnectInterval);
    };

    this.ws.onerror = () => {
      if (this.ws) {
        this.ws.close();
      }
    };
  }

  public subscribe(handler: MessageHandler): () => void {
    this.handlers.add(handler);
    return () => this.handlers.delete(handler);
  }

  private notifyHandlers(type: string, data: any) {
    this.handlers.forEach((h) => {
      try {
        h(type, data);
      } catch (err) {
        console.error('WebSocket handler error:', err);
      }
    });
  }
}

export const wsClient = new WebSocketClient();
