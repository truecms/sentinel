/**
 * Modules API service
 */

import { apiClient } from '@utils/api';
import type { PaginatedResponse } from '@types/base';

export interface ModuleUpdateInfo {
  has_security_update: boolean;
  sites_with_security_updates: number;
  sites_needing_regular_update: number;
}

export interface ModuleStatusItem {
  id: string;
  name: string;
  machine_name: string;
  module_type: string;
  current_version: string;
  latest_version: string;
  security_update: boolean;
  sites_affected: number;
  total_sites: number;
  last_updated: string;
  update_info: ModuleUpdateInfo;
}

export interface ModuleStatusResponse {
  total_modules: number;
  modules_with_updates: number;
  modules_with_security_updates: number;
  modules_up_to_date: number;
  last_updated: string;
}

export interface ModuleStatusParams {
  page?: number;
  page_size?: number;
  search?: string;
  security_only?: boolean;
  org_id?: number;
}

export const modulesApi = {
  // Get module status for dashboard table
  getDashboardStatus: async (params: ModuleStatusParams = {}): Promise<PaginatedResponse<ModuleStatusItem>> => {
    const response = await apiClient.get<PaginatedResponse<ModuleStatusItem>>('/modules/dashboard/status', { params });
    return response.data;
  },

  // Get module overview statistics
  getDashboardOverview: async (orgId?: number): Promise<ModuleStatusResponse> => {
    const params = orgId ? { org_id: orgId } : {};
    const response = await apiClient.get<ModuleStatusResponse>('/modules/dashboard/overview', { params });
    return response.data;
  },
};