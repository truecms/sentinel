import React, { useMemo } from 'react'
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  TooltipProps,
} from 'recharts'
import { motion } from 'framer-motion'
import type { TimelineChartProps } from '../../../../types/dashboard'
import { Skeleton } from '../../../common'

const CHART_COLORS = [
  '#3B82F6', // primary-500
  '#8B5CF6', // purple-500
  '#10B981', // success-500
  '#F59E0B', // warning-500
  '#EF4444', // danger-500
  '#06B6D4', // info-500
  '#EC4899', // pink-500
  '#F97316', // orange-500
]

export const TimelineChart: React.FC<TimelineChartProps> = ({
  data,
  type = 'line',
  period,
  metrics,
  height = 300,
  interactive = true,
  annotations = [],
  loading = false,
}) => {
  // Format data for Recharts
  const formattedData = useMemo(() => {
    // Group data by timestamp
    const groupedData = new Map<string, {
      timestamp: Date;
      formattedTime: string;
      [key: string]: Date | string | number;
    }>()
    
    data.forEach((point) => {
      const timestamp = point.timestamp.toISOString()
      if (!groupedData.has(timestamp)) {
        groupedData.set(timestamp, {
          timestamp: point.timestamp,
          formattedTime: formatTimestamp(point.timestamp, period),
        })
      }
      
      const dataPoint = groupedData.get(timestamp)
      if (dataPoint) {
        dataPoint[point.label || 'value'] = point.value
      }
    })
    
    return Array.from(groupedData.values()).sort(
      (a, b) => a.timestamp.getTime() - b.timestamp.getTime()
    )
  }, [data, period])
  
  // Get unique metrics from data
  const dataMetrics = useMemo(() => {
    if (metrics.length > 0) return metrics
    
    const uniqueMetrics = new Set<string>()
    data.forEach((point) => {
      uniqueMetrics.add(point.label || 'value')
    })
    return Array.from(uniqueMetrics)
  }, [data, metrics])
  
  function formatTimestamp(date: Date, period: 'hour' | 'day' | 'week' | 'month'): string {
    switch (period) {
      case 'hour':
        return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
      case 'day':
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
      case 'week':
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
      case 'month':
        return date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' })
      default:
        return date.toLocaleDateString('en-US')
    }
  }
  
  const CustomTooltip = ({ active, payload, label }: TooltipProps<number, string>) => {
    if (!active || !payload) return null
    
    return (
      <div className="bg-white dark:bg-neutral-800 p-3 rounded-lg shadow-lg dark:shadow-dark-lg border border-neutral-200 dark:border-neutral-700">
        <p className="text-sm font-medium text-neutral-900 dark:text-neutral-100 mb-1">{label}</p>
        {payload.map((entry, index) => (
          <div key={index} className="flex items-center gap-2 text-sm">
            <div 
              className="w-3 h-3 rounded-full" 
              style={{ backgroundColor: entry.color }}
            />
            <span className="text-neutral-600 dark:text-neutral-400">{entry.name}:</span>
            <span className="font-medium text-neutral-900 dark:text-neutral-100">
              {typeof entry.value === 'number' ? entry.value.toFixed(2) : entry.value}
            </span>
          </div>
        ))}
      </div>
    )
  }
  
  const renderChart = () => {
    const commonProps = {
      data: formattedData,
      margin: { top: 5, right: 5, left: 5, bottom: 5 },
    }
    
    const commonAxisProps = {
      stroke: '#737373', // neutral-500
      fontSize: 12,
    }
    
    const gridProps = {
      strokeDasharray: '3 3',
      stroke: '#E5E7EB', // neutral-200
    }
    
    switch (type) {
      case 'area':
        return (
          <AreaChart {...commonProps}>
            <CartesianGrid {...gridProps} />
            <XAxis dataKey="formattedTime" {...commonAxisProps} />
            <YAxis {...commonAxisProps} />
            {interactive && <Tooltip content={<CustomTooltip />} />}
            {annotations.map((annotation, index) => (
              <ReferenceLine
                key={index}
                x={formatTimestamp(annotation.timestamp, period)}
                stroke={annotation.color || '#737373'}
                strokeDasharray="5 5"
                label={{
                  value: annotation.label,
                  position: 'top',
                  fontSize: 12,
                }}
              />
            ))}
            {dataMetrics.map((metric, index) => (
              <Area
                key={metric}
                type="monotone"
                dataKey={metric}
                stroke={CHART_COLORS[index % CHART_COLORS.length]}
                fill={CHART_COLORS[index % CHART_COLORS.length]}
                fillOpacity={0.3}
                strokeWidth={2}
                animationDuration={1000}
                animationBegin={index * 100}
              />
            ))}
          </AreaChart>
        )
        
      case 'bar':
        return (
          <BarChart {...commonProps}>
            <CartesianGrid {...gridProps} />
            <XAxis dataKey="formattedTime" {...commonAxisProps} />
            <YAxis {...commonAxisProps} />
            {interactive && <Tooltip content={<CustomTooltip />} />}
            {annotations.map((annotation, index) => (
              <ReferenceLine
                key={index}
                x={formatTimestamp(annotation.timestamp, period)}
                stroke={annotation.color || '#737373'}
                strokeDasharray="5 5"
                label={{
                  value: annotation.label,
                  position: 'top',
                  fontSize: 12,
                }}
              />
            ))}
            {dataMetrics.map((metric, index) => (
              <Bar
                key={metric}
                dataKey={metric}
                fill={CHART_COLORS[index % CHART_COLORS.length]}
                animationDuration={1000}
                animationBegin={index * 100}
              />
            ))}
          </BarChart>
        )
        
      case 'line':
      default:
        return (
          <LineChart {...commonProps}>
            <CartesianGrid {...gridProps} />
            <XAxis dataKey="formattedTime" {...commonAxisProps} />
            <YAxis {...commonAxisProps} />
            {interactive && <Tooltip content={<CustomTooltip />} />}
            {annotations.map((annotation, index) => (
              <ReferenceLine
                key={index}
                x={formatTimestamp(annotation.timestamp, period)}
                stroke={annotation.color || '#737373'}
                strokeDasharray="5 5"
                label={{
                  value: annotation.label,
                  position: 'top',
                  fontSize: 12,
                }}
              />
            ))}
            {dataMetrics.map((metric, index) => (
              <Line
                key={metric}
                type="monotone"
                dataKey={metric}
                stroke={CHART_COLORS[index % CHART_COLORS.length]}
                strokeWidth={2}
                dot={false}
                animationDuration={1000}
                animationBegin={index * 100}
              />
            ))}
          </LineChart>
        )
    }
  }
  
  if (loading) {
    return (
      <Skeleton 
        height={height} 
        className="rounded-lg w-full"
      />
    )
  }
  
  if (data.length === 0) {
    return (
      <div 
        className="bg-neutral-50 dark:bg-neutral-900 rounded-lg flex items-center justify-center text-neutral-500 dark:text-neutral-400"
        style={{ height }}
      >
        No data available
      </div>
    )
  }
  
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
      className="w-full"
    >
      <ResponsiveContainer width="100%" height={height}>
        {renderChart()}
      </ResponsiveContainer>
      
      {/* Legend */}
      {dataMetrics.length > 1 && (
        <div className="flex flex-wrap gap-4 mt-4 justify-center">
          {dataMetrics.map((metric, index) => (
            <div key={metric} className="flex items-center gap-2">
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: CHART_COLORS[index % CHART_COLORS.length] }}
              />
              <span className="text-sm text-neutral-600 dark:text-neutral-400">{metric}</span>
            </div>
          ))}
        </div>
      )}
    </motion.div>
  )
}