import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  X, 
  AlertCircle, 
  CheckCircle, 
  AlertTriangle, 
  Info,
  ChevronRight
} from 'lucide-react';
import { Button } from '../Button';

export interface AlertProps {
  type: 'info' | 'success' | 'warning' | 'error';
  title: string;
  message?: string;
  dismissible?: boolean;
  onDismiss?: () => void;
  action?: {
    label: string;
    onClick: () => void;
  };
  className?: string;
  banner?: boolean;
}

const iconMap = {
  info: Info,
  success: CheckCircle,
  warning: AlertTriangle,
  error: AlertCircle,
};

const colorMap = {
  info: {
    bg: 'bg-info-50 dark:bg-info-900/10',
    border: 'border-info-200 dark:border-info-800',
    icon: 'text-info-600 dark:text-info-400',
    title: 'text-info-900 dark:text-info-100',
    message: 'text-info-700 dark:text-info-300',
  },
  success: {
    bg: 'bg-success-50 dark:bg-success-900/10',
    border: 'border-success-200 dark:border-success-800',
    icon: 'text-success-600 dark:text-success-400',
    title: 'text-success-900 dark:text-success-100',
    message: 'text-success-700 dark:text-success-300',
  },
  warning: {
    bg: 'bg-warning-50 dark:bg-warning-900/10',
    border: 'border-warning-200 dark:border-warning-800',
    icon: 'text-warning-600 dark:text-warning-400',
    title: 'text-warning-900 dark:text-warning-100',
    message: 'text-warning-700 dark:text-warning-300',
  },
  error: {
    bg: 'bg-danger-50 dark:bg-danger-900/10',
    border: 'border-danger-200 dark:border-danger-800',
    icon: 'text-danger-600 dark:text-danger-400',
    title: 'text-danger-900 dark:text-danger-100',
    message: 'text-danger-700 dark:text-danger-300',
  },
};

export const Alert: React.FC<AlertProps> = ({
  type,
  title,
  message,
  dismissible = false,
  onDismiss,
  action,
  className = '',
  banner = false,
}) => {
  const [isVisible, setIsVisible] = useState(true);
  const Icon = iconMap[type];
  const colors = colorMap[type];

  const handleDismiss = () => {
    setIsVisible(false);
    setTimeout(() => {
      onDismiss?.();
    }, 300);
  };

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ opacity: 0, y: banner ? -20 : 0, scale: banner ? 1 : 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: banner ? -20 : 0, scale: banner ? 1 : 0.95 }}
          transition={{ duration: 0.2 }}
          className={`
            ${banner ? 'w-full' : 'rounded-lg'}
            ${colors.bg}
            border
            ${colors.border}
            ${banner ? 'px-4 py-3 sm:px-6' : 'p-4'}
            ${className}
          `}
          role="alert"
        >
          <div className="flex">
            <div className="flex-shrink-0">
              <Icon className={`h-5 w-5 ${colors.icon}`} aria-hidden="true" />
            </div>
            <div className="ml-3 flex-1">
              <h3 className={`text-sm font-medium ${colors.title}`}>
                {title}
              </h3>
              {message && (
                <div className={`mt-1 text-sm ${colors.message}`}>
                  {message}
                </div>
              )}
              {action && (
                <div className="mt-3">
                  <Button
                    size="sm"
                    variant={type === 'error' ? 'danger' : type === 'warning' ? 'warning' : 'primary'}
                    onClick={action.onClick}
                    className="inline-flex items-center"
                  >
                    {action.label}
                    <ChevronRight className="ml-1 h-4 w-4" />
                  </Button>
                </div>
              )}
            </div>
            {dismissible && (
              <div className="ml-auto pl-3">
                <div className="-mx-1.5 -my-1.5">
                  <button
                    type="button"
                    onClick={handleDismiss}
                    className={`
                      inline-flex rounded-md p-1.5
                      ${colors.bg}
                      ${colors.icon}
                      hover:bg-opacity-75
                      focus:outline-none focus:ring-2 focus:ring-offset-2
                      focus:ring-${type}-600
                    `}
                  >
                    <span className="sr-only">Dismiss</span>
                    <X className="h-5 w-5" aria-hidden="true" />
                  </button>
                </div>
              </div>
            )}
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};