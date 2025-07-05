import React, { useMemo, useState } from 'react'
import { motion } from 'framer-motion'
import { clsx } from 'clsx'
import type { RiskHeatmapProps, RiskData } from '../../../../types/dashboard'

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
    critical: '#991b1b',
    high: '#dc2626',
    medium: '#f59e0b',
    low: '#fbbf24',
    info: '#3b82f6',
  }
  
  const getColorForCell = (cell: RiskData | undefined) => {
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
    return defaultColorScale[cell.severity] || '#e5e7eb'
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
        <div className="animate-pulse">
          <div className="grid gap-1" style={{
            gridTemplateColumns: `auto repeat(${xAxis.length}, ${cellSize}px)`,
            gridTemplateRows: `auto repeat(${yAxis.length}, ${cellSize}px)`,
          }}>
            {/* Header row */}
            <div /> {/* Empty corner cell */}
            {xAxis.map((_, index) => (
              <div key={index} className="h-8 bg-gray-200 rounded" />
            ))}
            
            {/* Data rows */}
            {yAxis.map((_, yIndex) => (
              <React.Fragment key={yIndex}>
                <div className="w-20 h-full bg-gray-200 rounded" />
                {xAxis.map((_, xIndex) => (
                  <div
                    key={`${xIndex}-${yIndex}`}
                    className="bg-gray-200 rounded"
                    style={{ width: cellSize, height: cellSize }}
                  />
                ))}
              </React.Fragment>
            ))}
          </div>
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
                'flex items-center justify-center text-gray-700 font-medium',
                fontSize
              )}
              style={{ writingMode: cellSize < 30 ? 'vertical-rl' : 'horizontal-tb' }}
            >
              {label}
            </div>
          ))}
          
          {/* Data rows */}
          {yAxis.map((yLabel, yIndex) => (
            <React.Fragment key={yLabel}>
              {/* Y-axis header */}
              <div
                className={clsx(
                  'flex items-center px-2 text-gray-700 font-medium truncate',
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
                      isHovered && 'ring-2 ring-gray-900 ring-opacity-50'
                    )}
                    style={{
                      backgroundColor: getColorForCell(cell),
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
                          ? 'text-gray-800' 
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
                          className="bg-gray-900 text-white p-2 rounded-lg shadow-lg whitespace-nowrap"
                        >
                          <div className="absolute top-full left-1/2 -translate-x-1/2 -mt-1">
                            <div className="w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-900" />
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
          <span className="text-sm text-gray-600">Risk Level:</span>
          <div className="flex items-center gap-4">
            {Object.entries(defaultColorScale).map(([level, color]) => (
              <div key={level} className="flex items-center gap-2">
                <div
                  className="w-4 h-4 rounded"
                  style={{ backgroundColor: color }}
                />
                <span className="text-sm text-gray-600 capitalize">{level}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}