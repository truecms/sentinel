import { LucideIcon } from 'lucide-react'

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
  timestamp: Date
  value: number
  label?: string
}

export interface ChartAnnotation {
  timestamp: Date
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