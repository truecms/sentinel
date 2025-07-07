import React from 'react';
import { motion } from 'framer-motion';
import { LucideIcon } from 'lucide-react';

interface FeatureCardProps {
  icon: LucideIcon;
  title: string;
  description: string;
  features?: string[];
  color?: 'primary' | 'secondary' | 'success' | 'warning' | 'danger' | 'info';
  delay?: number;
  className?: string;
}

export const FeatureCard: React.FC<FeatureCardProps> = ({
  icon: Icon,
  title,
  description,
  features = [],
  color = 'primary',
  delay = 0,
  className = '',
}) => {
  const colorClasses = {
    primary: 'bg-primary-100 text-primary-600 dark:bg-primary-900 dark:text-primary-400',
    secondary: 'bg-secondary-100 text-secondary-600 dark:bg-secondary-900 dark:text-secondary-400',
    success: 'bg-success-100 text-success-600 dark:bg-success-900 dark:text-success-400',
    warning: 'bg-warning-100 text-warning-600 dark:bg-warning-900 dark:text-warning-400',
    danger: 'bg-danger-100 text-danger-600 dark:bg-danger-900 dark:text-danger-400',
    info: 'bg-info-100 text-info-600 dark:bg-info-900 dark:text-info-400',
  };

  const borderColors = {
    primary: 'hover:border-primary-200 dark:hover:border-primary-800',
    secondary: 'hover:border-secondary-200 dark:hover:border-secondary-800',
    success: 'hover:border-success-200 dark:hover:border-success-800',
    warning: 'hover:border-warning-200 dark:hover:border-warning-800',
    danger: 'hover:border-danger-200 dark:hover:border-danger-800',
    info: 'hover:border-info-200 dark:hover:border-info-800',
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay, ease: 'easeOut' }}
      whileHover={{ y: -5 }}
      className={`
        group relative bg-white dark:bg-neutral-800 rounded-xl p-6 lg:p-8
        border border-neutral-200 dark:border-neutral-700
        shadow-sm hover:shadow-xl transition-all duration-300
        ${borderColors[color]}
        ${className}
      `}
    >
      {/* Icon */}
      <div className={`
        inline-flex items-center justify-center w-14 h-14 rounded-lg mb-6
        ${colorClasses[color]}
        transition-transform duration-300 group-hover:scale-110
      `}>
        <Icon className="w-7 h-7" />
      </div>

      {/* Title */}
      <h3 className="text-xl font-semibold text-neutral-900 dark:text-white mb-3">
        {title}
      </h3>

      {/* Description */}
      <p className="text-neutral-600 dark:text-neutral-300 mb-4 leading-relaxed">
        {description}
      </p>

      {/* Features List */}
      {features.length > 0 && (
        <ul className="space-y-2 mt-4">
          {features.map((feature, index) => (
            <li
              key={index}
              className="flex items-start text-sm text-neutral-500 dark:text-neutral-400"
            >
              <svg
                className={`w-4 h-4 mr-2 flex-shrink-0 mt-0.5 ${
                  color === 'primary' ? 'text-primary-500' : 
                  color === 'secondary' ? 'text-secondary-500' : 
                  color === 'success' ? 'text-success-500' : 
                  color === 'warning' ? 'text-warning-500' : 
                  color === 'danger' ? 'text-danger-500' : 
                  'text-info-500'
                }`}
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                  clipRule="evenodd"
                />
              </svg>
              <span>{feature}</span>
            </li>
          ))}
        </ul>
      )}

      {/* Hover Effect Border */}
      <div
        className={`
          absolute inset-0 rounded-xl opacity-0 group-hover:opacity-100
          transition-opacity duration-300 pointer-events-none
          ${color === 'primary' ? 'bg-gradient-to-br from-primary-500/10 to-primary-600/10' : 
            color === 'secondary' ? 'bg-gradient-to-br from-secondary-500/10 to-secondary-600/10' : 
            color === 'success' ? 'bg-gradient-to-br from-success-500/10 to-success-600/10' : 
            color === 'warning' ? 'bg-gradient-to-br from-warning-500/10 to-warning-600/10' : 
            color === 'danger' ? 'bg-gradient-to-br from-danger-500/10 to-danger-600/10' : 
            'bg-gradient-to-br from-info-500/10 to-info-600/10'}
        `}
      />
    </motion.div>
  );
};