import React from 'react';
import { motion } from 'framer-motion';
import { Check, X, Star } from 'lucide-react';
import { Button } from '../../common/Button';

interface Feature {
  text: string;
  included: boolean;
  tooltip?: string;
}

interface PricingCardProps {
  name: string;
  description: string;
  price: string | number;
  priceUnit?: string;
  currency?: string;
  features: Feature[] | string[];
  recommended?: boolean;
  ctaText?: string;
  ctaHref?: string;
  delay?: number;
  isAnnual?: boolean;
  monthlyPrice?: string | number;
  annualSavings?: string;
  className?: string;
}

export const PricingCard: React.FC<PricingCardProps> = ({
  name,
  description,
  price,
  priceUnit = '/month',
  currency = '$',
  features,
  recommended = false,
  ctaText = 'Get Started',
  ctaHref = '/signup',
  delay = 0,
  isAnnual = false,
  monthlyPrice,
  annualSavings,
  className = '',
}) => {
  const normalizedFeatures: Feature[] = features.map((feature) =>
    typeof feature === 'string' ? { text: feature, included: true } : feature
  );

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay, ease: 'easeOut' }}
      whileHover={{ y: -5 }}
      className={`
        relative bg-white dark:bg-neutral-800 rounded-xl
        ${recommended ? 'ring-2 ring-primary-500 shadow-xl' : 'border border-neutral-200 dark:border-neutral-700 shadow-sm'}
        hover:shadow-2xl transition-all duration-300
        ${className}
      `}
    >
      {/* Recommended Badge */}
      {recommended && (
        <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
          <div className="bg-primary-500 text-white px-4 py-1 rounded-full text-sm font-semibold flex items-center">
            <Star className="w-4 h-4 mr-1 fill-current" />
            Most Popular
          </div>
        </div>
      )}

      <div className="p-6 lg:p-8">
        {/* Header */}
        <div className="text-center mb-6">
          <h3 className="text-2xl font-bold text-neutral-900 dark:text-white mb-2">
            {name}
          </h3>
          <p className="text-neutral-600 dark:text-neutral-300">
            {description}
          </p>
        </div>

        {/* Pricing */}
        <div className="text-center mb-8">
          <div className="flex items-baseline justify-center">
            <span className="text-xl text-neutral-600 dark:text-neutral-400">
              {currency}
            </span>
            <span className="text-5xl font-bold text-neutral-900 dark:text-white mx-1">
              {price}
            </span>
            <span className="text-neutral-600 dark:text-neutral-400">
              {priceUnit}
            </span>
          </div>
          
          {/* Annual/Monthly Toggle Info */}
          {isAnnual && monthlyPrice && (
            <div className="mt-2 space-y-1">
              <p className="text-sm text-neutral-500 dark:text-neutral-400 line-through">
                {currency}{monthlyPrice} monthly
              </p>
              {annualSavings && (
                <p className="text-sm text-success-600 dark:text-success-400 font-medium">
                  Save {annualSavings}
                </p>
              )}
            </div>
          )}
        </div>

        {/* CTA Button */}
        <a href={ctaHref} className="block mb-8">
          <Button
            variant={recommended ? 'primary' : 'outline'}
            fullWidth
            size="lg"
          >
            {ctaText}
          </Button>
        </a>

        {/* Features */}
        <div className="space-y-3">
          {normalizedFeatures.map((feature, index) => (
            <div
              key={index}
              className={`flex items-start ${
                feature.included ? '' : 'opacity-50'
              }`}
            >
              {feature.included ? (
                <Check className="w-5 h-5 text-success-500 dark:text-success-400 mr-3 flex-shrink-0 mt-0.5" />
              ) : (
                <X className="w-5 h-5 text-neutral-400 dark:text-neutral-500 mr-3 flex-shrink-0 mt-0.5" />
              )}
              <div className="flex-1">
                <span className={`text-sm ${
                  feature.included
                    ? 'text-neutral-700 dark:text-neutral-300'
                    : 'text-neutral-500 dark:text-neutral-400'
                }`}>
                  {feature.text}
                </span>
                {feature.tooltip && (
                  <p className="text-xs text-neutral-500 dark:text-neutral-400 mt-0.5">
                    {feature.tooltip}
                  </p>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Background Glow for Recommended */}
      {recommended && (
        <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-primary-500/10 to-secondary-500/10 pointer-events-none" />
      )}
    </motion.div>
  );
};