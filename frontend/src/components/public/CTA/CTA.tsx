import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowRight, Sparkles } from 'lucide-react';
import { Button } from '../../common/Button';

interface CTAProps {
  title: string;
  subtitle?: string;
  primaryButton?: {
    text: string;
    href: string;
  };
  secondaryButton?: {
    text: string;
    href: string;
  };
  variant?: 'default' | 'gradient' | 'dark';
  backgroundPattern?: boolean;
  className?: string;
}

export const CTA: React.FC<CTAProps> = ({
  title,
  subtitle,
  primaryButton = { text: 'Get Started', href: '/signup' },
  secondaryButton,
  variant = 'gradient',
  backgroundPattern = true,
  className = '',
}) => {
  const variants = {
    default: 'bg-neutral-50 dark:bg-neutral-900',
    gradient: 'bg-gradient-to-r from-primary-600 to-secondary-600 dark:from-primary-500 dark:to-secondary-500',
    dark: 'bg-neutral-900 dark:bg-neutral-800',
  };

  const textColors = {
    default: 'text-neutral-900 dark:text-white',
    gradient: 'text-white',
    dark: 'text-white',
  };

  const subtitleColors = {
    default: 'text-neutral-600 dark:text-neutral-300',
    gradient: 'text-white/90',
    dark: 'text-neutral-300',
  };

  return (
    <section className={`relative overflow-hidden ${className}`}>
      <div className={`py-16 lg:py-24 ${variants[variant]}`}>
        {/* Background Pattern */}
        {backgroundPattern && variant === 'gradient' && (
          <div className="absolute inset-0 opacity-10">
            <div className="absolute inset-0 bg-[url('data:image/svg+xml,%3Csvg%20width%3D%2260%22%20height%3D%2260%22%20viewBox%3D%220%200%2060%2060%22%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%3E%3Cg%20fill%3D%22none%22%20fill-rule%3D%22evenodd%22%3E%3Cg%20fill%3D%22%23ffffff%22%20fill-opacity%3D%220.4%22%3E%3Cpath%20d%3D%22M36%2034v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6%2034v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6%204V0H4v4H0v2h4v4h2V6h4V4H6z%22%2F%3E%3C%2Fg%3E%3C%2Fg%3E%3C%2Fsvg%3E')]" />
          </div>
        )}

        <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="max-w-3xl mx-auto text-center"
          >
            {/* Sparkle Icon */}
            {variant === 'gradient' && (
              <motion.div
                initial={{ scale: 0, rotate: -180 }}
                animate={{ scale: 1, rotate: 0 }}
                transition={{ duration: 0.8, type: 'spring' }}
                className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-white/20 backdrop-blur-sm mb-6"
              >
                <Sparkles className="w-8 h-8 text-white" />
              </motion.div>
            )}

            {/* Title */}
            <h2 className={`text-3xl sm:text-4xl lg:text-5xl font-bold mb-4 ${textColors[variant]}`}>
              {title}
            </h2>

            {/* Subtitle */}
            {subtitle && (
              <p className={`text-lg sm:text-xl mb-8 ${subtitleColors[variant]}`}>
                {subtitle}
              </p>
            )}

            {/* Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link to={primaryButton.href}>
                <Button
                  size="lg"
                  variant={variant === 'gradient' ? 'secondary' : 'primary'}
                  rightIcon={<ArrowRight className="w-5 h-5" />}
                  className={variant === 'gradient' ? 'bg-white text-primary-600 hover:bg-neutral-100' : ''}
                >
                  {primaryButton.text}
                </Button>
              </Link>
              
              {secondaryButton && (
                <Link to={secondaryButton.href}>
                  <Button
                    size="lg"
                    variant="outline"
                    className={
                      variant === 'gradient'
                        ? 'border-white text-white hover:bg-white/10'
                        : variant === 'dark'
                        ? 'border-neutral-600 text-white hover:bg-neutral-700'
                        : ''
                    }
                  >
                    {secondaryButton.text}
                  </Button>
                </Link>
              )}
            </div>

            {/* Trust Text */}
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.6, delay: 0.3 }}
              className={`mt-6 text-sm ${
                variant === 'gradient' ? 'text-white/80' : 'text-neutral-500 dark:text-neutral-400'
              }`}
            >
              No credit card required • 14-day free trial • Cancel anytime
            </motion.p>
          </motion.div>
        </div>

        {/* Decorative Elements */}
        {variant === 'gradient' && (
          <>
            <div className="absolute top-0 left-0 w-40 h-40 bg-white/10 rounded-full blur-3xl" />
            <div className="absolute bottom-0 right-0 w-60 h-60 bg-white/10 rounded-full blur-3xl" />
          </>
        )}
      </div>
    </section>
  );
};