import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  Activity, 
  Shield, 
  AlertTriangle, 
  TrendingUp,
  Package,
  Server,
  Globe,
  BarChart3
} from 'lucide-react'
import { 
  MetricCard, 
  SecurityGauge, 
  ModuleStatusTable 
} from '../../components/dashboard/widgets'
import { 
  TimelineChart, 
  RiskHeatmap 
} from '../../components/dashboard/charts'
import type { 
  ModuleStatus, 
  TimeSeriesData, 
  RiskData 
} from '../../types/dashboard'

// Mock data for demo purposes
const mockModules: ModuleStatus[] = [
  {
    id: '1',
    name: 'views',
    currentVersion: '8.9.20',
    latestVersion: '8.10.1',
    securityUpdate: true,
    lastUpdated: new Date('2024-01-15'),
    sites: 45,
  },
  {
    id: '2',
    name: 'token',
    currentVersion: '8.9.20',
    latestVersion: '8.9.20',
    securityUpdate: false,
    lastUpdated: new Date('2024-01-10'),
    sites: 38,
  },
  {
    id: '3',
    name: 'pathauto',
    currentVersion: '8.9.18',
    latestVersion: '8.9.20',
    securityUpdate: false,
    lastUpdated: new Date('2024-01-05'),
    sites: 42,
  },
]

const mockTimelineData: TimeSeriesData[] = [
  { timestamp: new Date('2024-01-01'), value: 95, label: 'Security Score' },
  { timestamp: new Date('2024-01-02'), value: 92, label: 'Security Score' },
  { timestamp: new Date('2024-01-03'), value: 88, label: 'Security Score' },
  { timestamp: new Date('2024-01-04'), value: 90, label: 'Security Score' },
  { timestamp: new Date('2024-01-05'), value: 85, label: 'Security Score' },
  { timestamp: new Date('2024-01-06'), value: 87, label: 'Security Score' },
  { timestamp: new Date('2024-01-07'), value: 92, label: 'Security Score' },
]

const mockRiskData: RiskData[][] = [
  [
    { value: 85, label: '85', severity: 'high' },
    { value: 45, label: '45', severity: 'medium' },
    { value: 20, label: '20', severity: 'low' },
  ],
  [
    { value: 95, label: '95', severity: 'critical' },
    { value: 70, label: '70', severity: 'high' },
    { value: 30, label: '30', severity: 'low' },
  ],
  [
    { value: 60, label: '60', severity: 'medium' },
    { value: 40, label: '40', severity: 'medium' },
    { value: 15, label: '15', severity: 'info' },
  ],
]

export const Dashboard: React.FC = () => {
  const [selectedPeriod, setSelectedPeriod] = useState<'day' | 'week' | 'month'>('week')

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 },
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold text-neutral-900 dark:text-neutral-100">
          Dashboard
        </h1>
        <p className="mt-2 text-neutral-600 dark:text-neutral-400">
          Monitor your Drupal sites security and performance
        </p>
      </div>

      {/* Metric Cards */}
      <motion.div
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        <motion.div variants={itemVariants}>
          <MetricCard
            title="Active Sites"
            value="127"
            change={{ value: 12, type: 'increase', period: 'from last month' }}
            icon={Globe}
            color="info"
          />
        </motion.div>
        <motion.div variants={itemVariants}>
          <MetricCard
            title="Security Updates"
            value="8"
            change={{ value: 23, type: 'decrease', period: 'from last week' }}
            icon={Shield}
            color="warning"
          />
        </motion.div>
        <motion.div variants={itemVariants}>
          <MetricCard
            title="Modules Tracked"
            value="342"
            change={{ value: 5, type: 'increase', period: 'from last month' }}
            icon={Package}
            color="success"
          />
        </motion.div>
        <motion.div variants={itemVariants}>
          <MetricCard
            title="Critical Issues"
            value="3"
            change={{ value: 50, type: 'increase', period: 'from yesterday' }}
            icon={AlertTriangle}
            color="danger"
          />
        </motion.div>
      </motion.div>

      {/* Security and Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Security Gauge */}
        <motion.div
          className="bg-white dark:bg-neutral-800 rounded-lg border border-neutral-200 dark:border-neutral-700 shadow-sm dark:shadow-dark-sm p-6"
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2 }}
        >
          <h2 className="text-lg font-semibold text-neutral-900 dark:text-neutral-100 mb-4">
            Overall Security Score
          </h2>
          <SecurityGauge
            score={87}
            label="Security Score"
            thresholds={{ critical: 25, warning: 50, good: 75 }}
            size="large"
          />
        </motion.div>

        {/* Timeline Chart */}
        <motion.div
          className="lg:col-span-2 bg-white dark:bg-neutral-800 rounded-lg border border-neutral-200 dark:border-neutral-700 shadow-sm dark:shadow-dark-sm p-6"
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.3 }}
        >
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-neutral-900 dark:text-neutral-100">
              Security Trend
            </h2>
            <div className="flex gap-2">
              {(['day', 'week', 'month'] as const).map((period) => (
                <button
                  key={period}
                  onClick={() => setSelectedPeriod(period)}
                  className={`px-3 py-1 text-sm rounded-lg transition-colors ${
                    selectedPeriod === period
                      ? 'bg-primary-100 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300'
                      : 'text-neutral-600 dark:text-neutral-400 hover:bg-neutral-100 dark:hover:bg-neutral-700'
                  }`}
                >
                  {period.charAt(0).toUpperCase() + period.slice(1)}
                </button>
              ))}
            </div>
          </div>
          <TimelineChart
            data={mockTimelineData}
            type="area"
            period={selectedPeriod}
            metrics={['Security Score']}
            height={250}
          />
        </motion.div>
      </div>

      {/* Module Status Table */}
      <motion.div
        className="bg-white dark:bg-neutral-800 rounded-lg border border-neutral-200 dark:border-neutral-700 shadow-sm dark:shadow-dark-sm"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
      >
        <div className="p-6 border-b border-neutral-200 dark:border-neutral-700">
          <h2 className="text-lg font-semibold text-neutral-900 dark:text-neutral-100">
            Module Status Overview
          </h2>
        </div>
        <ModuleStatusTable
          modules={mockModules}
          pagination={{
            page: 1,
            pageSize: 10,
            total: mockModules.length,
            onPageChange: () => {},
          }}
          sorting={{
            field: 'lastUpdated',
            direction: 'desc',
            onSort: () => {},
          }}
          filters={{
            searchTerm: '',
            securityOnly: false,
            onFilterChange: () => {},
          }}
        />
      </motion.div>

      {/* Risk Heatmap */}
      <motion.div
        className="bg-white dark:bg-neutral-800 rounded-lg border border-neutral-200 dark:border-neutral-700 shadow-sm dark:shadow-dark-sm p-6"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
      >
        <h2 className="text-lg font-semibold text-neutral-900 dark:text-neutral-100 mb-4">
          Risk Matrix by Site
        </h2>
        <RiskHeatmap
          data={mockRiskData}
          xAxis={['Site A', 'Site B', 'Site C']}
          yAxis={['Security', 'Performance', 'Updates']}
          tooltip={(data) => (
            <div>
              <div className="font-semibold">{data.label}</div>
              <div className="text-xs">Risk Score: {data.value}</div>
            </div>
          )}
        />
      </motion.div>
    </div>
  )
}