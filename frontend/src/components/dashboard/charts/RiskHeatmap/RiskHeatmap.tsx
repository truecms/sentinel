import React, { useMemo, useState } from 'react'
import { motion } from 'framer-motion'
import { clsx } from 'clsx'
import type { RiskHeatmapProps, RiskData } from '../../../../types/dashboard'
import { Skeleton } from '../../../common'

// Utility function to create abbreviations from site names
const abbreviateSiteName = (siteName: string): string => {
  // Split by spaces and common separators
  const words = siteName.split(/[\s\-_]+/)
  
  if (words.length === 1) {
    // Single word: take first 3 characters
    return words[0].substring(0, 3).toUpperCase()
  }
  
  // Multiple words: take first letter of each word
  const abbreviation = words
    .filter(word => word.length > 0)
    .map(word => word.charAt(0).toUpperCase())
    .join('')
  
  // If abbreviation is too long, limit to 4 characters
  return abbreviation.length > 4 ? abbreviation.substring(0, 4) : abbreviation
}

export const RiskHeatmap: React.FC<RiskHeatmapProps> = ({
  data,
  xAxis,
  yAxis,
  colorScale,
  tooltip,
  onCellClick,
  loading = false,
}) => {
  const [hoveredCell, setHoveredCell] = useState<{ x: number; y: number } | null>(null)
  
  // Default color scale based on severity
  const defaultColorScale = {
    critical: 'bg-danger-700 dark:bg-danger-600',
    high: 'bg-danger-500 dark:bg-danger-400',
    medium: 'bg-warning-500 dark:bg-warning-400',
    low: 'bg-warning-300 dark:bg-warning-300',
    info: 'bg-info-500 dark:bg-info-400',
  }
  
  const defaultColorValues = {
    critical: '#991b1b',
    high: '#dc2626',
    medium: '#f59e0b',
    low: '#fbbf24',
    info: '#3b82f6',
  }
  
  const getColorClassForCell = (cell: RiskData | undefined) => {
    if (!cell) return 'bg-neutral-100 dark:bg-neutral-800' // empty cell color
    
    // Use severity-based colors
    return defaultColorScale[cell.severity] || 'bg-neutral-200 dark:bg-neutral-700'
  }
  
  const getColorValueForCell = (cell: RiskData | undefined) => {
    if (!cell) return '#f3f4f6' // empty cell color
    
    if (colorScale && cell.value !== undefined) {
      // Use custom color scale if provided
      const { min, max, steps } = colorScale
      if (steps && steps.length > 0) {
        const stepSize = 100 / (steps.length - 1)
        const stepIndex = Math.min(
          Math.floor(cell.value / stepSize),
          steps.length - 1
        )
        return steps[stepIndex]
      }
      // Linear interpolation between min and max
      return cell.value > 50 ? max : min
    }
    
    // Use severity-based colors
    return defaultColorValues[cell.severity] || '#e5e7eb'
  }
  
  const cellSize = useMemo(() => {
    const maxWidth = 800 // max container width
    const maxHeight = 600 // max container height
    const xSize = Math.min(50, Math.floor(maxWidth / xAxis.length))
    const ySize = Math.min(50, Math.floor(maxHeight / yAxis.length))
    return Math.min(xSize, ySize, 40) // cap at 40px
  }, [xAxis, yAxis])
  
  const fontSize = cellSize < 30 ? 'text-xs' : 'text-sm'
  
  if (loading) {
    return (
      <div className="p-4">
        <div className="grid gap-1" style={{
          gridTemplateColumns: `auto repeat(${xAxis.length}, ${cellSize}px)`,
          gridTemplateRows: `auto repeat(${yAxis.length}, ${cellSize}px)`,
        }}>
          {/* Header row */}
          <div /> {/* Empty corner cell */}
          {xAxis.map((_, index) => (
            <Skeleton key={index} width={cellSize} height="2rem" />
          ))}
          
          {/* Data rows */}
          {yAxis.map((_, yIndex) => (
            <React.Fragment key={yIndex}>
              <Skeleton width="5rem" height={cellSize} />
              {xAxis.map((_, xIndex) => (
                <Skeleton
                  key={`${xIndex}-${yIndex}`}
                  width={cellSize}
                  height={cellSize}
                  className="rounded"
                />
              ))}
            </React.Fragment>
          ))}
        </div>
      </div>
    )
  }
  
  return (
    <div className="overflow-auto">
      <div className="inline-block min-w-full">
        <div
          className="grid gap-1 p-4"
          style={{
            gridTemplateColumns: `minmax(100px, auto) repeat(${xAxis.length}, ${cellSize}px)`,
            gridTemplateRows: `auto repeat(${yAxis.length}, ${cellSize}px)`,
          }}
        >
          {/* Corner cell */}
          <div />
          
          {/* X-axis headers */}
          {xAxis.map((label) => (
            <div
              key={label}
              className={clsx(
                'flex items-center justify-center text-neutral-700 dark:text-neutral-300 font-medium relative group cursor-help',
                fontSize
              )}
              style={{ writingMode: cellSize < 30 ? 'vertical-rl' : 'horizontal-tb' }}
            >
              {abbreviateSiteName(label)}
              {/* Tooltip with full site name */}
              <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-2 py-1 text-xs bg-neutral-900 dark:bg-neutral-700 text-white rounded whitespace-nowrap opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity z-50">
                {label}
                <div className="absolute top-full left-1/2 -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-neutral-900 dark:border-t-neutral-700"></div>
              </div>
            </div>
          ))}
          
          {/* Data rows */}
          {yAxis.map((yLabel, yIndex) => (
            <React.Fragment key={yLabel}>
              {/* Y-axis header */}
              <div
                className={clsx(
                  'flex items-center px-2 text-neutral-700 dark:text-neutral-300 font-medium truncate',
                  fontSize
                )}
              >
                {yLabel}
              </div>
              
              {/* Data cells */}
              {xAxis.map((xLabel, xIndex) => {
                const cell = data[yIndex]?.[xIndex]
                const isHovered = hoveredCell?.x === xIndex && hoveredCell?.y === yIndex
                
                return (
                  <motion.div
                    key={`${xIndex}-${yIndex}`}
                    className={clsx(
                      'relative rounded cursor-pointer transition-all duration-200',
                      cell && 'hover:shadow-lg hover:z-10',
                      isHovered && 'ring-2 ring-neutral-900 dark:ring-neutral-100 ring-opacity-50',
                      colorScale ? '' : getColorClassForCell(cell)
                    )}
                    style={{
                      backgroundColor: colorScale ? getColorValueForCell(cell) : undefined,
                      width: cellSize,
                      height: cellSize,
                    }}
                    onClick={() => cell && onCellClick?.(xIndex, yIndex)}
                    onMouseEnter={() => setHoveredCell({ x: xIndex, y: yIndex })}
                    onMouseLeave={() => setHoveredCell(null)}
                    whileHover={cell ? { scale: 1.05 } : undefined}
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{
                      delay: (yIndex * xAxis.length + xIndex) * 0.01,
                      duration: 0.3,
                    }}
                  >
                    {/* Cell value */}
                    {cell && (
                      <div className={clsx(
                        'absolute inset-0 flex items-center justify-center font-medium',
                        cell.severity === 'low' || cell.severity === 'info' 
                          ? 'text-neutral-800 dark:text-neutral-900' 
                          : 'text-white',
                        fontSize
                      )}>
                        {cell.value}
                      </div>
                    )}
                    
                    {/* Tooltip */}
                    {cell && isHovered && tooltip && (
                      <div className="absolute z-20 bottom-full left-1/2 -translate-x-1/2 mb-2">
                        <motion.div
                          initial={{ opacity: 0, y: 10 }}
                          animate={{ opacity: 1, y: 0 }}
                          className="bg-neutral-900 dark:bg-neutral-800 text-white p-2 rounded-lg shadow-lg dark:shadow-dark-lg whitespace-nowrap"
                        >
                          <div className="absolute top-full left-1/2 -translate-x-1/2 -mt-1">
                            <div className="w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-neutral-900 dark:border-t-neutral-800" />
                          </div>
                          {tooltip(cell)}
                        </motion.div>
                      </div>
                    )}
                  </motion.div>
                )
              })}
            </React.Fragment>
          ))}
        </div>
        
        {/* Legend */}
        <div className="mt-6 flex items-center justify-center gap-6">
          <span className="text-sm text-neutral-600 dark:text-neutral-400">Risk Level:</span>
          <div className="flex items-center gap-4">
            {Object.entries(defaultColorScale).map(([level, colorClass]) => (
              <div key={level} className="flex items-center gap-2">
                <div
                  className={clsx('w-4 h-4 rounded', colorClass)}
                />
                <span className="text-sm text-neutral-600 dark:text-neutral-400 capitalize">{level}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}