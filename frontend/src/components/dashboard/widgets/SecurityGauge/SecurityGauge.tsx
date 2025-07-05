import React, { useMemo } from 'react'
import { motion } from 'framer-motion'
import { clsx } from 'clsx'
import type { SecurityGaugeProps } from '../../../../types/dashboard'

export const SecurityGauge: React.FC<SecurityGaugeProps> = ({
  score,
  label,
  thresholds,
  size = 'medium',
  animated = true,
}) => {
  const normalizedScore = Math.min(Math.max(score, 0), 100)
  
  const sizeConfig = {
    small: { width: 120, height: 60, strokeWidth: 8 },
    medium: { width: 180, height: 90, strokeWidth: 12 },
    large: { width: 240, height: 120, strokeWidth: 16 },
  }
  
  const { width, height, strokeWidth } = sizeConfig[size]
  const radius = (Math.min(width, height * 2) - strokeWidth) / 2
  const centerX = width / 2
  const centerY = height
  
  // Calculate arc path
  const startAngle = -Math.PI
  const endAngle = 0
  const angle = startAngle + (normalizedScore / 100) * (endAngle - startAngle)
  
  const pathData = useMemo(() => {
    const x1 = centerX + radius * Math.cos(startAngle)
    const y1 = centerY + radius * Math.sin(startAngle)
    const x2 = centerX + radius * Math.cos(angle)
    const y2 = centerY + radius * Math.sin(angle)
    
    const largeArcFlag = angle - startAngle <= Math.PI ? '0' : '1'
    
    return `M ${x1} ${y1} A ${radius} ${radius} 0 ${largeArcFlag} 1 ${x2} ${y2}`
  }, [angle, centerX, centerY, radius, startAngle])
  
  const backgroundPath = useMemo(() => {
    const x1 = centerX + radius * Math.cos(startAngle)
    const y1 = centerY + radius * Math.sin(startAngle)
    const x2 = centerX + radius * Math.cos(endAngle)
    const y2 = centerY + radius * Math.sin(endAngle)
    
    return `M ${x1} ${y1} A ${radius} ${radius} 0 1 1 ${x2} ${y2}`
  }, [centerX, centerY, radius, startAngle, endAngle])
  
  // Determine color based on thresholds
  const getColor = () => {
    if (normalizedScore >= thresholds.good) return '#10b981' // success
    if (normalizedScore >= thresholds.warning) return '#f59e0b' // warning
    return '#ef4444' // danger
  }
  
  const textSizeClasses = {
    small: 'text-lg',
    medium: 'text-2xl',
    large: 'text-3xl',
  }
  
  const labelSizeClasses = {
    small: 'text-xs',
    medium: 'text-sm',
    large: 'text-base',
  }
  
  return (
    <div className="flex flex-col items-center">
      <svg width={width} height={height + 10} className="overflow-visible">
        {/* Background arc */}
        <path
          d={backgroundPath}
          fill="none"
          stroke="#e5e7eb"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
        />
        
        {/* Score arc */}
        <motion.path
          d={pathData}
          fill="none"
          stroke={getColor()}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          initial={animated ? { pathLength: 0 } : { pathLength: 1 }}
          animate={{ pathLength: 1 }}
          transition={{ duration: 1, ease: 'easeOut' }}
        />
        
        {/* Threshold markers */}
        {[thresholds.critical, thresholds.warning, thresholds.good].map((threshold) => {
          const markerAngle = startAngle + (threshold / 100) * (endAngle - startAngle)
          const x1 = centerX + (radius - strokeWidth / 2) * Math.cos(markerAngle)
          const y1 = centerY + (radius - strokeWidth / 2) * Math.sin(markerAngle)
          const x2 = centerX + (radius + strokeWidth / 2) * Math.cos(markerAngle)
          const y2 = centerY + (radius + strokeWidth / 2) * Math.sin(markerAngle)
          
          return (
            <line
              key={threshold}
              x1={x1}
              y1={y1}
              x2={x2}
              y2={y2}
              stroke="#6b7280"
              strokeWidth={2}
            />
          )
        })}
      </svg>
      
      {/* Score text */}
      <div className="text-center -mt-4">
        <motion.div
          className={clsx('font-bold text-gray-900', textSizeClasses[size])}
          initial={animated ? { opacity: 0 } : { opacity: 1 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
        >
          {normalizedScore}%
        </motion.div>
        <div className={clsx('text-gray-500 uppercase tracking-wider mt-1', labelSizeClasses[size])}>
          {label}
        </div>
      </div>
    </div>
  )
}