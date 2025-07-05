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

const CHART_COLORS = [
  '#3b82f6', // primary blue
  '#8b5cf6', // purple
  '#10b981', // green
  '#f59e0b', // amber
  '#ef4444', // red
  '#06b6d4', // cyan
  '#ec4899', // pink
  '#f97316', // orange
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
      <div className="bg-white p-3 rounded-lg shadow-lg border">
        <p className="text-sm font-medium text-gray-900 mb-1">{label}</p>
        {payload.map((entry, index) => (
          <div key={index} className="flex items-center gap-2 text-sm">
            <div 
              className="w-3 h-3 rounded-full" 
              style={{ backgroundColor: entry.color }}
            />
            <span className="text-gray-600">{entry.name}:</span>
            <span className="font-medium text-gray-900">
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
      stroke: '#9ca3af',
      fontSize: 12,
    }
    
    const gridProps = {
      strokeDasharray: '3 3',
      stroke: '#e5e7eb',
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
                stroke={annotation.color || '#6b7280'}
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
                stroke={annotation.color || '#6b7280'}
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
                stroke={annotation.color || '#6b7280'}
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
      <div 
        className="bg-gray-100 rounded-lg animate-pulse"
        style={{ height }}
      />
    )
  }
  
  if (data.length === 0) {
    return (
      <div 
        className="bg-gray-50 rounded-lg flex items-center justify-center text-gray-500"
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
              <span className="text-sm text-gray-600">{metric}</span>
            </div>
          ))}
        </div>
      )}
    </motion.div>
  )
}