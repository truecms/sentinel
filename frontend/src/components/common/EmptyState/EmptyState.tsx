import React from 'react';
import { motion } from 'framer-motion';
import { FileX, Search, Shield, AlertCircle } from 'lucide-react';
import { Button } from '../Button';

export interface EmptyStateProps {
  title: string;
  description?: string;
  icon?: 'default' | 'search' | 'security' | 'error' | React.ReactNode;
  action?: {
    label: string;
    onClick: () => void;
  };
  className?: string;
}

const iconMap = {
  default: FileX,
  search: Search,
  security: Shield,
  error: AlertCircle,
};

export const EmptyState: React.FC<EmptyStateProps> = ({
  title,
  description,
  icon = 'default',
  action,
  className = '',
}) => {
  const IconComponent = typeof icon === 'string' ? iconMap[icon] : null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`flex flex-col items-center justify-center p-8 text-center ${className}`}
    >
      <div className="mb-4">
        {typeof icon === 'string' && IconComponent ? (
          <IconComponent className="w-12 h-12 text-neutral-400 dark:text-neutral-600" />
        ) : (
          icon
        )}
      </div>
      
      <h3 className="text-lg font-semibold text-neutral-900 dark:text-neutral-100 mb-2">
        {title}
      </h3>
      
      {description && (
        <p className="text-sm text-neutral-600 dark:text-neutral-400 mb-6 max-w-sm">
          {description}
        </p>
      )}
      
      {action && (
        <Button onClick={action.onClick} variant="primary" size="sm">
          {action.label}
        </Button>
      )}
    </motion.div>
  );
};