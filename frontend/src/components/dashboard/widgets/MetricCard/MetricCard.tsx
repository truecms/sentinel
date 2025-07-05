import React from 'react'
import { motion } from 'framer-motion'
import { TrendingUp, TrendingDown } from 'lucide-react'
import { clsx } from 'clsx'
import type { MetricCardProps } from '../../../../types/dashboard'

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  change,
  icon: Icon,
  color = 'info',
  loading = false,
  onClick,
}) => {
  const colorClasses = {
    success: 'bg-green-50 text-green-600 border-green-200',
    warning: 'bg-amber-50 text-amber-600 border-amber-200',
    danger: 'bg-red-50 text-red-600 border-red-200',
    info: 'bg-blue-50 text-blue-600 border-blue-200',
  }

  const changeColorClasses = {
    increase: 'text-green-600',
    decrease: 'text-red-600',
  }

  const cardClasses = clsx(
    'relative p-6 bg-white rounded-lg border shadow-sm transition-all duration-200',
    onClick && 'cursor-pointer hover:shadow-md',
    loading && 'animate-pulse'
  )

  const iconContainerClasses = clsx(
    'absolute top-6 right-6 p-3 rounded-lg',
    colorClasses[color]
  )

  return (
    <motion.div
      className={cardClasses}
      onClick={onClick}
      whileHover={onClick ? { scale: 1.02 } : undefined}
      whileTap={onClick ? { scale: 0.98 } : undefined}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      {Icon && (
        <div className={iconContainerClasses}>
          <Icon className="w-6 h-6" />
        </div>
      )}

      <div className="pr-16">
        <p className="text-sm font-medium text-gray-500 uppercase tracking-wider">
          {title}
        </p>

        {loading ? (
          <div className="mt-2">
            <div className="h-8 w-24 bg-gray-200 rounded animate-pulse" />
          </div>
        ) : (
          <p className="mt-2 text-3xl font-bold text-gray-900">
            {value}
          </p>
        )}

        {change && !loading && (
          <div className={clsx('mt-4 flex items-center gap-1', changeColorClasses[change.type])}>
            {change.type === 'increase' ? (
              <TrendingUp className="w-4 h-4" />
            ) : (
              <TrendingDown className="w-4 h-4" />
            )}
            <span className="text-sm font-medium">
              {change.value > 0 ? '+' : ''}{change.value}%
            </span>
            <span className="text-sm text-gray-500 ml-1">
              {change.period}
            </span>
          </div>
        )}
      </div>
    </motion.div>
  )
}