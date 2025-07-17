/**
 * Dashboard API service
 */

import { apiClient } from '@utils/api';
import type { 
  DashboardOverview, 
  SecurityDashboard, 
  SiteDashboard, 
  ActivityItem, 
  TimeSeriesData 
} from '@types/dashboard';

export const dashboardApi = {
  // Get dashboard overview
  getOverview: async (orgId?: number): Promise<DashboardOverview> => {
    const params = orgId ? { org_id: orgId } : {};
    const response = await apiClient.get<DashboardOverview>('/dashboard/overview', { params });
    return response.data;
  },

  // Get security dashboard
  getSecurity: async (orgId?: number): Promise<SecurityDashboard> => {
    const params = orgId ? { org_id: orgId } : {};
    const response = await apiClient.get<SecurityDashboard>('/dashboard/security', { params });
    return response.data;
  },

  // Get site dashboard
  getSite: async (siteId: number): Promise<SiteDashboard> => {
    const response = await apiClient.get<SiteDashboard>(`/dashboard/site/${siteId}`);
    return response.data;
  },

  // Get recent activity
  getActivity: async (orgId?: number, limit = 20): Promise<ActivityItem[]> => {
    const params = { limit, ...(orgId && { org_id: orgId }) };
    const response = await apiClient.get<ActivityItem[]>('/dashboard/activity', { params });
    return response.data;
  },

  // Get metric trends
  getTrends: async (
    metric: string,
    period: 'hour' | 'day' | 'week' | 'month' = 'day',
    points = 30,
    orgId?: number
  ): Promise<TimeSeriesData[]> => {
    const params = { 
      period, 
      points, 
      ...(orgId && { org_id: orgId }) 
    };
    const response = await apiClient.get<TimeSeriesData[]>(`/dashboard/trends/${metric}`, { params });
    return response.data;
  },

  // Get WebSocket status (admin only)
  getWebSocketStatus: async () => {
    const response = await apiClient.get('/ws/status');
    return response.data;
  },

  // Get risk matrix data
  getRiskMatrix: async (orgId?: number, limit = 10): Promise<any> => {
    const params = { limit, ...(orgId && { org_id: orgId }) };
    const response = await apiClient.get('/risk-matrix', { params });
    return response.data;
  },
};