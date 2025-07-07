import React from 'react';
import { motion } from 'framer-motion';

export interface CardProps {
  children: React.ReactNode;
  className?: string;
  padding?: 'none' | 'sm' | 'md' | 'lg';
  hoverable?: boolean;
  clickable?: boolean;
  onClick?: () => void;
}

const paddingClasses = {
  none: '',
  sm: 'p-4',
  md: 'p-6',
  lg: 'p-8',
};

export const Card: React.FC<CardProps> = ({
  children,
  className = '',
  padding = 'md',
  hoverable = false,
  clickable = false,
  onClick,
}) => {
  const Component = clickable ? motion.button : motion.div;
  
  return (
    <Component
      className={`
        card
        ${paddingClasses[padding]}
        ${hoverable || clickable ? 'card-hover cursor-pointer' : ''}
        ${className}
      `}
      onClick={onClick}
      whileHover={hoverable || clickable ? { scale: 1.02 } : undefined}
      whileTap={clickable ? { scale: 0.98 } : undefined}
    >
      {children}
    </Component>
  );
};