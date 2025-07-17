/**
 * WebSocket service for real-time dashboard updates
 */

import { toast } from 'react-hot-toast';
import TokenStorageService from '@services/tokenStorage';

// WebSocket message types
export enum MessageType {
  CONNECTED = 'connected',
  DISCONNECTED = 'disconnected',
  ERROR = 'error',
  SUBSCRIBE = 'subscribe',
  UNSUBSCRIBE = 'unsubscribe',
  SUBSCRIBED = 'subscribed',
  UNSUBSCRIBED = 'unsubscribed',
  PING = 'ping',
  PONG = 'pong',
  DIRECT = 'direct',
  BROADCAST = 'broadcast',
}

// WebSocket channels
export enum DashboardChannel {
  SECURITY_ALERTS = 'security.alerts',
  METRIC_UPDATES = 'metrics.updates',
  SYSTEM_STATUS = 'system.status',
  ORG_METRICS = 'org.{}.metrics',
  ORG_ACTIVITY = 'org.{}.activity',
  SITE_STATUS = 'site.{}.status',
  SITE_MODULES = 'site.{}.modules',
}

// WebSocket message interfaces
export interface WebSocketMessage {
  type: MessageType;
  timestamp: string;
  data?: any;
  channel?: string;
}

export interface SubscriptionMessage {
  type: MessageType.SUBSCRIBE | MessageType.UNSUBSCRIBE;
  channel: string;
}

export interface BroadcastMessage {
  channel: string;
  data: any;
  timestamp: string;
}

// Callback types
export type SubscriptionCallback = (data: any) => void;
export type ConnectionCallback = (connected: boolean) => void;
export type ErrorCallback = (error: string) => void;

export class WebSocketService {
  private ws: WebSocket | null = null;
  private wsUrl: string;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private subscriptions: Map<string, Set<SubscriptionCallback>> = new Map();
  private connectionCallbacks: Set<ConnectionCallback> = new Set();
  private errorCallbacks: Set<ErrorCallback> = new Set();
  private pingInterval: NodeJS.Timeout | null = null;
  private isManualClose = false;

  constructor(baseUrl: string = '') {
    // Use environment variable for WebSocket URL
    const envWsUrl = import.meta.env.VITE_WS_URL;
    if (envWsUrl) {
      this.wsUrl = `${envWsUrl}/dashboard`;
    } else {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const host = baseUrl || window.location.host;
      this.wsUrl = `${protocol}//${host}/api/v1/ws/dashboard`;
    }
  }

  /**
   * Connect to WebSocket server
   */
  async connect(): Promise<void> {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      return;
    }

    const token = TokenStorageService.getToken();
    if (!token) {
      throw new Error('No authentication token available');
    }

    this.isManualClose = false;
    const wsUrl = `${this.wsUrl}?token=${encodeURIComponent(token)}`;
    
    return new Promise((resolve, reject) => {
      this.ws = new WebSocket(wsUrl);
      
      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.reconnectAttempts = 0;
        this.notifyConnectionCallbacks(true);
        this.startPingInterval();
        resolve();
      };

      this.ws.onmessage = (event) => {
        this.handleMessage(event.data);
      };

      this.ws.onclose = (event) => {
        console.log('WebSocket disconnected:', event.code, event.reason);
        this.cleanup();
        this.notifyConnectionCallbacks(false);
        
        if (!this.isManualClose) {
          this.handleReconnect();
        }
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.notifyErrorCallbacks('WebSocket connection error');
        reject(new Error('WebSocket connection failed'));
      };
    });
  }

  /**
   * Disconnect from WebSocket server
   */
  disconnect(): void {
    this.isManualClose = true;
    this.cleanup();
    
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  /**
   * Subscribe to a channel
   */
  subscribe(channel: string, callback: SubscriptionCallback): () => void {
    // Add callback to subscriptions
    if (!this.subscriptions.has(channel)) {
      this.subscriptions.set(channel, new Set());
    }
    this.subscriptions.get(channel)!.add(callback);

    // Send subscription message if connected
    if (this.isConnected()) {
      this.sendMessage({
        type: MessageType.SUBSCRIBE,
        channel,
      });
    }

    // Return unsubscribe function
    return () => this.unsubscribe(channel, callback);
  }

  /**
   * Unsubscribe from a channel
   */
  unsubscribe(channel: string, callback: SubscriptionCallback): void {
    const callbacks = this.subscriptions.get(channel);
    if (callbacks) {
      callbacks.delete(callback);
      
      // If no more callbacks, unsubscribe from channel
      if (callbacks.size === 0) {
        this.subscriptions.delete(channel);
        
        if (this.isConnected()) {
          this.sendMessage({
            type: MessageType.UNSUBSCRIBE,
            channel,
          });
        }
      }
    }
  }

  /**
   * Add connection status callback
   */
  onConnectionChange(callback: ConnectionCallback): () => void {
    this.connectionCallbacks.add(callback);
    
    // Call immediately with current status
    callback(this.isConnected());
    
    return () => {
      this.connectionCallbacks.delete(callback);
    };
  }

  /**
   * Add error callback
   */
  onError(callback: ErrorCallback): () => void {
    this.errorCallbacks.add(callback);
    
    return () => {
      this.errorCallbacks.delete(callback);
    };
  }

  /**
   * Check if WebSocket is connected
   */
  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }

  /**
   * Get connection status
   */
  getConnectionStatus(): 'connecting' | 'connected' | 'disconnected' | 'reconnecting' {
    if (!this.ws) return 'disconnected';
    
    switch (this.ws.readyState) {
      case WebSocket.CONNECTING:
        return this.reconnectAttempts > 0 ? 'reconnecting' : 'connecting';
      case WebSocket.OPEN:
        return 'connected';
      case WebSocket.CLOSING:
      case WebSocket.CLOSED:
        return 'disconnected';
      default:
        return 'disconnected';
    }
  }

  /**
   * Handle incoming messages
   */
  private handleMessage(data: string): void {
    try {
      const message: WebSocketMessage = JSON.parse(data);
      
      switch (message.type) {
        case MessageType.CONNECTED:
          // Resubscribe to all channels after connection
          this.resubscribeToChannels();
          break;
          
        case MessageType.SUBSCRIBED:
          console.log(`Subscribed to channel: ${message.channel}`);
          break;
          
        case MessageType.UNSUBSCRIBED:
          console.log(`Unsubscribed from channel: ${message.channel}`);
          break;
          
        case MessageType.ERROR:
          console.error('WebSocket server error:', message.data);
          this.notifyErrorCallbacks(message.data || 'Server error');
          break;
          
        case MessageType.PONG:
          // Pong received, connection is alive
          break;
          
        case MessageType.DIRECT:
          // Direct message to this client
          this.handleDirectMessage(message.data);
          break;
          
        default:
          // Channel broadcast message
          if (message.channel) {
            this.handleChannelMessage(message.channel, message.data);
          }
      }
    } catch (error) {
      console.error('Error parsing WebSocket message:', error);
    }
  }

  /**
   * Handle direct messages
   */
  private handleDirectMessage(data: any): void {
    // Handle direct messages like notifications
    if (data.type === 'notification') {
      this.showNotification(data);
    }
  }

  /**
   * Handle channel messages
   */
  private handleChannelMessage(channel: string, data: any): void {
    const callbacks = this.subscriptions.get(channel);
    if (callbacks) {
      callbacks.forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error('Error in subscription callback:', error);
        }
      });
    }
  }

  /**
   * Send message to server
   */
  private sendMessage(message: any): void {
    if (this.isConnected()) {
      this.ws!.send(JSON.stringify(message));
    }
  }

  /**
   * Resubscribe to all channels after reconnection
   */
  private resubscribeToChannels(): void {
    for (const channel of this.subscriptions.keys()) {
      this.sendMessage({
        type: MessageType.SUBSCRIBE,
        channel,
      });
    }
  }

  /**
   * Start ping interval to keep connection alive
   */
  private startPingInterval(): void {
    this.pingInterval = setInterval(() => {
      if (this.isConnected()) {
        this.sendMessage({ type: MessageType.PING });
      }
    }, 30000); // Ping every 30 seconds
  }

  /**
   * Handle reconnection logic
   */
  private handleReconnect(): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      const delay = Math.min(
        this.reconnectDelay * Math.pow(2, this.reconnectAttempts),
        30000
      );
      
      console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts + 1}/${this.maxReconnectAttempts})`);
      
      setTimeout(async () => {
        this.reconnectAttempts++;
        try {
          await this.connect();
        } catch (error) {
          console.error('Reconnection failed:', error);
        }
      }, delay);
    } else {
      console.error('Max reconnection attempts reached');
      this.notifyErrorCallbacks('Connection lost. Please refresh the page.');
      
      // Show toast notification
      toast.error('Connection lost. Please refresh the page to reconnect.');
    }
  }

  /**
   * Cleanup resources
   */
  private cleanup(): void {
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
      this.pingInterval = null;
    }
  }

  /**
   * Notify connection callbacks
   */
  private notifyConnectionCallbacks(connected: boolean): void {
    this.connectionCallbacks.forEach(callback => {
      try {
        callback(connected);
      } catch (error) {
        console.error('Error in connection callback:', error);
      }
    });
  }

  /**
   * Notify error callbacks
   */
  private notifyErrorCallbacks(error: string): void {
    this.errorCallbacks.forEach(callback => {
      try {
        callback(error);
      } catch (error) {
        console.error('Error in error callback:', error);
      }
    });
  }

  /**
   * Show notification
   */
  private showNotification(notification: any): void {
    const { title, message, severity = 'info' } = notification;
    
    switch (severity) {
      case 'critical':
      case 'high':
        toast.error(`${title}: ${message}`);
        break;
      case 'warning':
      case 'medium':
        toast.error(`${title}: ${message}`);
        break;
      case 'info':
      case 'low':
        toast.success(`${title}: ${message}`);
        break;
      default:
        toast(message);
    }
  }
}

// Create singleton instance
export const websocketService = new WebSocketService();