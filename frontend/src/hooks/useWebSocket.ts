/**
 * React hooks for WebSocket integration
 */

import { useEffect, useState, useCallback, useRef } from 'react';
import { useSelector } from 'react-redux';
import { websocketService, DashboardChannel } from '@services/websocket';
import type { SubscriptionCallback } from '@services/websocket';
import { selectIsAuthenticated } from '@features/auth/authSlice';

// Hook to manage WebSocket connection
export function useWebSocketConnection() {
  const [isConnected, setIsConnected] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected' | 'reconnecting'>('disconnected');
  const [error, setError] = useState<string | null>(null);
  const isAuthenticated = useSelector(selectIsAuthenticated);

  useEffect(() => {
    if (!isAuthenticated) {
      websocketService.disconnect();
      setIsConnected(false);
      setConnectionStatus('disconnected');
      return;
    }

    // Connect to WebSocket - disabled for now until backend is ready
    const connectWebSocket = async () => {
      try {
        setConnectionStatus('connecting');
        // TODO: Enable when WebSocket backend is implemented
        // await websocketService.connect();
        setConnectionStatus('disconnected');
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Connection failed');
        setConnectionStatus('disconnected');
      }
    };

    connectWebSocket();

    // Listen for connection changes
    const unsubscribeConnection = websocketService.onConnectionChange(setIsConnected);
    const unsubscribeError = websocketService.onError(setError);

    // Update connection status
    const statusInterval = setInterval(() => {
      setConnectionStatus(websocketService.getConnectionStatus());
    }, 1000);

    return () => {
      unsubscribeConnection();
      unsubscribeError();
      clearInterval(statusInterval);
    };
  }, [isAuthenticated]);

  const reconnect = useCallback(async () => {
    if (isAuthenticated) {
      try {
        setError(null);
        setConnectionStatus('connecting');
        // TODO: Enable when WebSocket backend is implemented
        // await websocketService.connect();
        setConnectionStatus('disconnected');
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Reconnection failed');
        setConnectionStatus('disconnected');
      }
    }
  }, [isAuthenticated]);

  return {
    isConnected,
    connectionStatus,
    error,
    reconnect,
  };
}

// Hook to subscribe to WebSocket channels
export function useWebSocketSubscription(
  channel: string,
  callback: SubscriptionCallback,
  dependencies: React.DependencyList = []
) {
  const callbackRef = useRef(callback);
  const { isConnected } = useWebSocketConnection();

  // Update callback ref when callback changes
  useEffect(() => {
    callbackRef.current = callback;
  }, [callback]);
  
  // React to dependency changes
  useEffect(() => {
    callbackRef.current = callback;
  }, dependencies); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (!isConnected || !channel) {
      return;
    }

    // Wrap callback to use current ref
    const wrappedCallback = (data: unknown) => {
      callbackRef.current(data);
    };

    // Subscribe to channel
    const unsubscribe = websocketService.subscribe(channel, wrappedCallback);

    return unsubscribe;
  }, [channel, isConnected]);
}

// Hook for dashboard metrics updates
export function useDashboardMetrics(orgId?: number) {
  const [metrics, setMetrics] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const channel = orgId 
    ? DashboardChannel.ORG_METRICS.replace('{}', orgId.toString())
    : DashboardChannel.METRIC_UPDATES;

  const handleMetricsUpdate = useCallback((data: unknown) => {
    if (typeof data === 'object' && data !== null) {
      setMetrics(prevMetrics => ({
        ...prevMetrics,
        ...(data as Record<string, unknown>),
      }));
      setLoading(false);
      setError(null);
    }
  }, []);

  useWebSocketSubscription(channel, handleMetricsUpdate, []);

  return { metrics, loading, error };
}

// Hook for security alerts
export function useSecurityAlerts() {
  const [alerts, setAlerts] = useState<unknown[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);

  const handleSecurityAlert = useCallback((alert: unknown) => {
    setAlerts(prev => [alert, ...prev.slice(0, 49)]); // Keep last 50 alerts
    setUnreadCount(prev => prev + 1);
  }, []);

  useWebSocketSubscription(DashboardChannel.SECURITY_ALERTS, handleSecurityAlert, []);

  const markAsRead = useCallback(() => {
    setUnreadCount(0);
  }, []);

  const clearAlerts = useCallback(() => {
    setAlerts([]);
    setUnreadCount(0);
  }, []);

  return {
    alerts,
    unreadCount,
    markAsRead,
    clearAlerts,
  };
}

// Hook for site status updates
export function useSiteStatus(siteId: number) {
  const [status, setStatus] = useState<unknown>(null);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

  const channel = DashboardChannel.SITE_STATUS.replace('{}', siteId.toString());

  const handleStatusUpdate = useCallback((data: unknown) => {
    setStatus(data);
    setLastUpdate(new Date());
  }, []);

  useWebSocketSubscription(channel, handleStatusUpdate, [siteId]);

  return { status, lastUpdate };
}

// Hook for site module updates
export function useSiteModules(siteId: number) {
  const [modules, setModules] = useState<unknown[]>([]);
  const [pendingUpdates, setPendingUpdates] = useState(0);

  const channel = DashboardChannel.SITE_MODULES.replace('{}', siteId.toString());

  const handleModuleUpdate = useCallback((data: unknown) => {
    if (data.type === 'module_updated') {
      setModules(prev => 
        prev.map(module => 
          module.id === data.module.id ? { ...module, ...data.module } : module
        )
      );
    } else if (data.type === 'modules_sync') {
      setModules(data.modules);
      setPendingUpdates(data.pending_updates || 0);
    }
  }, []);

  useWebSocketSubscription(channel, handleModuleUpdate, [siteId]);

  return { modules, pendingUpdates };
}

// Hook for real-time notifications
export function useRealTimeNotifications() {
  const [notifications, setNotifications] = useState<unknown[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);

  const handleNotification = useCallback((notification: unknown) => {
    setNotifications(prev => [notification, ...prev.slice(0, 99)]); // Keep last 100
    setUnreadCount(prev => prev + 1);
  }, []);

  // Subscribe to multiple channels for notifications
  useWebSocketSubscription(DashboardChannel.SECURITY_ALERTS, handleNotification, []);
  useWebSocketSubscription(DashboardChannel.SYSTEM_STATUS, handleNotification, []);

  const markAsRead = useCallback(() => {
    setUnreadCount(0);
  }, []);

  const clearNotifications = useCallback(() => {
    setNotifications([]);
    setUnreadCount(0);
  }, []);

  return {
    notifications,
    unreadCount,
    markAsRead,
    clearNotifications,
  };
}

// Hook for organization activity
export function useOrganizationActivity(orgId: number) {
  const [activities, setActivities] = useState<unknown[]>([]);
  const [loading, setLoading] = useState(true);

  const channel = DashboardChannel.ORG_ACTIVITY.replace('{}', orgId.toString());

  const handleActivityUpdate = useCallback((data: unknown) => {
    if (data.type === 'activity_added') {
      setActivities(prev => [data.activity, ...prev.slice(0, 49)]); // Keep last 50
    } else if (data.type === 'activities_sync') {
      setActivities(data.activities);
    }
    setLoading(false);
  }, []);

  useWebSocketSubscription(channel, handleActivityUpdate, [orgId]);

  return { activities, loading };
}

// Hook for system status
export function useSystemStatus() {
  const [status, setStatus] = useState<unknown>(null);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

  const handleStatusUpdate = useCallback((data: unknown) => {
    setStatus(data);
    setLastUpdate(new Date());
  }, []);

  useWebSocketSubscription(DashboardChannel.SYSTEM_STATUS, handleStatusUpdate, []);

  return { status, lastUpdate };
}