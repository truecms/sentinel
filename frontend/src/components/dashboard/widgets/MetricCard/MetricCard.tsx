import React from 'react'
import { motion } from 'framer-motion'
import { TrendingUp, TrendingDown } from 'lucide-react'
import { clsx } from 'clsx'
import type { MetricCardProps } from '../../../../types/dashboard'
import { Skeleton } from '../../../common'

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
    success: 'bg-success-50 text-success-600 border-success-200 dark:bg-success-900/20 dark:text-success-400 dark:border-success-800',
    warning: 'bg-warning-50 text-warning-600 border-warning-200 dark:bg-warning-900/20 dark:text-warning-400 dark:border-warning-800',
    danger: 'bg-danger-50 text-danger-600 border-danger-200 dark:bg-danger-900/20 dark:text-danger-400 dark:border-danger-800',
    info: 'bg-info-50 text-info-600 border-info-200 dark:bg-info-900/20 dark:text-info-400 dark:border-info-800',
  }

  const changeColorClasses = {
    increase: 'text-success-600 dark:text-success-400',
    decrease: 'text-danger-600 dark:text-danger-400',
  }

  const cardClasses = clsx(
    'relative p-6 bg-white rounded-lg border shadow-sm transition-all duration-200',
    'dark:bg-neutral-800 dark:border-neutral-700 dark:shadow-dark-sm',
    onClick && 'cursor-pointer hover:shadow-md hover:scale-[1.02] dark:hover:shadow-dark-md',
    loading && 'animate-pulse'
  )

  const iconContainerClasses = clsx(
    'absolute top-6 right-6 p-3 rounded-lg border',
    colorClasses[color]
  )

  if (loading) {
    return (
      <div className={cardClasses}>
        <div className="pr-16">
          <Skeleton width="60%" height="1rem" className="mb-3" />
          <Skeleton width="80%" height="2rem" className="mb-4" />
          <Skeleton width="40%" height="1rem" />
        </div>
        <div className="absolute top-6 right-6">
          <Skeleton variant="circular" width="3rem" height="3rem" />
        </div>
      </div>
    )
  }

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
        <motion.div 
          className={iconContainerClasses}
          whileHover={{ rotate: 5 }}
          transition={{ type: "spring", stiffness: 300 }}
        >
          <Icon className="w-6 h-6" />
        </motion.div>
      )}

      <div className="pr-16">
        <p className="text-sm font-medium text-neutral-500 dark:text-neutral-400 uppercase tracking-wider">
          {title}
        </p>

        <p className="mt-2 text-3xl font-bold text-neutral-900 dark:text-neutral-100">
          {value}
        </p>

        {change && (
          <motion.div 
            className={clsx('mt-4 flex items-center gap-1', changeColorClasses[change.type])}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 }}
          >
            {change.type === 'increase' ? (
              <TrendingUp className="w-4 h-4" />
            ) : (
              <TrendingDown className="w-4 h-4" />
            )}
            <span className="text-sm font-medium">
              {change.value > 0 ? '+' : ''}{change.value}%
            </span>
            <span className="text-sm text-neutral-500 dark:text-neutral-400 ml-1">
              {change.period}
            </span>
          </motion.div>
        )}
      </div>
    </motion.div>
  )
}