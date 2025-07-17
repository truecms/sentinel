import type { LucideIcon } from 'lucide-react'

// Real-time dashboard types
export interface DashboardMetrics {
  totalSites: number
  securityScore: number
  criticalUpdates: number
  complianceRate: number
  vulnerabilities: VulnerabilityCount
}

export interface VulnerabilityCount {
  critical: number
  high: number
  medium: number
  low: number
}

export interface DashboardOverview {
  metrics: DashboardMetrics
  trends: Record<string, TimeSeriesData[]>
  topRisks: RiskItem[]
  recentActivity: ActivityItem[]
}

export interface SecurityDashboard {
  metrics: SecurityMetrics
  criticalModules: ModuleRiskItem[]
  vulnerabilityTimeline: TimeSeriesData[]
  recentPatches: ActivityItem[]
  alertQueue: ActivityItem[]
}

export interface SecurityMetrics {
  activeThreats: number
  unpatchedVulnerabilities: number
  averageTimeToPatch: number
  patchesAppliedToday: number
  pendingSecurityUpdates: number
  slaCompliance: number
}

export interface SiteDashboard {
  siteId: number
  siteName: string
  health: SiteHealth
  modules: SiteModuleStats
  timeline: ActivityItem[]
  recommendations: Recommendation[]
}

export interface SiteHealth {
  score: number
  status: 'healthy' | 'warning' | 'critical'
  lastSync: Date
}

export interface SiteModuleStats {
  total: number
  upToDate: number
  needsUpdate: number
  securityUpdates: number
}

export interface ActivityItem {
  id: string
  type: string
  title: string
  description?: string
  timestamp: Date
  severity?: 'critical' | 'high' | 'medium' | 'low' | 'info'
  metadata?: Record<string, unknown>
}

export interface RiskItem {
  id: string
  title: string
  riskScore: number
  affectedSites: number
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info'
  actionRequired: string
}

export interface ModuleRiskItem {
  moduleName: string
  moduleVersion: string
  riskScore: number
  affectedSites: number
  daysSinceUpdate: number
  hasSecurityUpdate: boolean
}

export interface Recommendation {
  id: string
  priority: 'critical' | 'high' | 'medium' | 'low' | 'info'
  title: string
  description: string
  action: string
}

// MetricCard Types
export interface MetricCardProps {
  title: string
  value: string | number
  change?: {
    value: number
    type: 'increase' | 'decrease'
    period: string
  }
  icon?: LucideIcon
  color?: 'success' | 'warning' | 'danger' | 'info'
  loading?: boolean
  onClick?: () => void
}

// SecurityGauge Types
export interface SecurityGaugeProps {
  score: number // 0-100
  label: string
  thresholds: {
    critical: number
    warning: number
    good: number
  }
  size?: 'small' | 'medium' | 'large'
  animated?: boolean
  loading?: boolean
}

// ModuleStatusTable Types
export interface ModuleStatus {
  id: string
  name: string
  currentVersion: string
  latestVersion?: string
  securityUpdate: boolean
  lastUpdated: Date
  sites: number
}

export interface PaginationConfig {
  page: number
  pageSize: number
  total: number
  onPageChange: (page: number) => void
}

export interface SortConfig {
  field: keyof ModuleStatus
  direction: 'asc' | 'desc'
  onSort: (field: keyof ModuleStatus) => void
}

export interface FilterConfig {
  searchTerm?: string
  securityOnly?: boolean
  onFilterChange: (filters: Partial<FilterConfig>) => void
}

export interface ModuleStatusTableProps {
  modules: ModuleStatus[]
  pagination?: PaginationConfig
  sorting?: SortConfig
  filters?: FilterConfig
  onRowClick?: (module: ModuleStatus) => void
  loading?: boolean
  error?: Error
}

// TimelineChart Types
export interface TimeSeriesData {
  timestamp: Date | string
  value: number
  label?: string
}

export interface ChartAnnotation {
  timestamp: Date | string
  label: string
  color?: string
}

export interface TimelineChartProps {
  data: TimeSeriesData[]
  type: 'line' | 'area' | 'bar'
  period: 'hour' | 'day' | 'week' | 'month'
  metrics: string[]
  height?: number
  interactive?: boolean
  annotations?: ChartAnnotation[]
  loading?: boolean
}

// RiskHeatmap Types
export interface RiskData {
  value: number
  label: string
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info'
}

export interface ColorScale {
  min: string
  max: string
  steps?: string[]
}

export interface RiskHeatmapProps {
  data: RiskData[][]
  xAxis: string[] // e.g., sites
  yAxis: string[] // e.g., modules
  colorScale?: ColorScale
  tooltip?: (data: RiskData) => React.ReactNode
  onCellClick?: (x: number, y: number) => void
  loading?: boolean
}