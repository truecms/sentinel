// API service for sites overview functionality
import { api } from '../utils/api'

export interface SiteOverview {
  id: number
  name: string
  url: string
  security_score: number
  total_modules_count: number
  security_updates_count: number
  non_security_updates_count: number
  last_data_push: string | null
  last_drupal_org_check: string | null
  status: 'healthy' | 'warning' | 'critical'
  organization_id: number
}

export interface SitesOverviewResponse {
  sites: SiteOverview[]
  pagination: {
    page: number
    per_page: number
    total: number
    total_pages: number
  }
  filters: {
    search?: string
    sort_by?: string
    sort_order?: 'asc' | 'desc'
  }
}

export interface SitesOverviewParams {
  skip?: number
  limit?: number
  search?: string
  sort_by?: string
  sort_order?: 'asc' | 'desc'
}

export const sitesApi = {
  // Get sites overview with pagination and filtering
  async getOverview(params: SitesOverviewParams = {}): Promise<SitesOverviewResponse> {
    const searchParams = new URLSearchParams()
    
    if (params.skip !== undefined) searchParams.set('skip', params.skip.toString())
    if (params.limit !== undefined) searchParams.set('limit', params.limit.toString())
    if (params.search) searchParams.set('search', params.search)
    if (params.sort_by) searchParams.set('sort_by', params.sort_by)
    if (params.sort_order) searchParams.set('sort_order', params.sort_order)
    
    const response = await api.get(`/sites/overview?${searchParams.toString()}`)
    return response.data
  },

  // Get individual site details
  async getSite(siteId: number) {
    const response = await api.get(`/sites/${siteId}`)
    return response.data
  },

  // Create new site
  async createSite(siteData: { name: string; url: string; organization_id: number }) {
    const response = await api.post('/sites', siteData)
    return response.data
  },

  // Update site
  async updateSite(siteId: number, siteData: Partial<{ name: string; url: string; organization_id: number }>) {
    const response = await api.put(`/sites/${siteId}`, siteData)
    return response.data
  },

  // Delete site
  async deleteSite(siteId: number) {
    const response = await api.delete(`/sites/${siteId}`)
    return response.data
  }
}