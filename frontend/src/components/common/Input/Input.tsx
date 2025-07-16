import React, { forwardRef, InputHTMLAttributes } from 'react';
import { cn } from '@utils/cn';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helpText?: string;
  leftIcon?: React.ComponentType<{ className?: string }>;
  rightElement?: React.ReactNode;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, helpText, leftIcon: LeftIcon, rightElement, className, ...props }, ref) => {
    return (
      <div className="w-full">
        {label && (
          <label 
            htmlFor={props.id} 
            className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
          >
            {label}
          </label>
        )}
        <div className="relative">
          {LeftIcon && (
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <LeftIcon className="h-5 w-5 text-gray-400 dark:text-gray-500" />
            </div>
          )}
          <input
            ref={ref}
            className={cn(
              'block w-full rounded-md border-gray-300 shadow-sm transition-colors',
              'focus:border-primary-500 focus:ring-primary-500 dark:focus:border-primary-400 dark:focus:ring-primary-400',
              'dark:bg-gray-900 dark:border-gray-700 dark:text-white dark:placeholder-gray-400',
              'disabled:cursor-not-allowed disabled:opacity-50',
              LeftIcon && 'pl-10',
              rightElement && 'pr-10',
              error && 'border-danger focus:border-danger focus:ring-danger dark:border-danger dark:focus:border-danger dark:focus:ring-danger',
              className
            )}
            {...props}
          />
          {rightElement && (
            <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
              {rightElement}
            </div>
          )}
        </div>
        {helpText && !error && (
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">{helpText}</p>
        )}
        {error && (
          <p className="mt-1 text-sm text-danger dark:text-danger">{error}</p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';