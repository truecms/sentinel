import React from 'react';
import { motion } from 'framer-motion';
import { Check, X } from 'lucide-react';
import { Link } from 'react-router-dom';

interface PricingCardProps {
  name: string;
  price: string | number;
  period?: string;
  description: string;
  features: string[];
  limitations?: string[];
  recommended?: boolean;
  ctaText: string;
  ctaLink: string;
  index?: number;
}

const PricingCard: React.FC<PricingCardProps> = ({
  name,
  price,
  period = 'per month',
  description,
  features,
  limitations = [],
  recommended = false,
  ctaText,
  ctaLink,
  index = 0
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5, delay: index * 0.1 }}
      className={`relative bg-white dark:bg-gray-800 rounded-xl shadow-lg hover:shadow-xl transition-shadow ${
        recommended ? 'ring-2 ring-blue-600 transform scale-105' : ''
      }`}
    >
      {recommended && (
        <div className="absolute -top-4 left-1/2 -translate-x-1/2">
          <span className="bg-blue-600 text-white px-4 py-1 rounded-full text-sm font-medium">
            Recommended
          </span>
        </div>
      )}

      <div className="p-8">
        <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          {name}
        </h3>
        <p className="text-gray-600 dark:text-gray-400 mb-6">
          {description}
        </p>

        <div className="mb-6">
          <span className="text-4xl font-bold text-gray-900 dark:text-white">
            {typeof price === 'number' ? `$${price}` : price}
          </span>
          {typeof price === 'number' && (
            <span className="text-gray-600 dark:text-gray-400 ml-2">
              {period}
            </span>
          )}
        </div>

        <ul className="space-y-3 mb-8">
          {features.map((feature, featureIndex) => (
            <li key={featureIndex} className="flex items-start gap-3">
              <Check className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
              <span className="text-gray-700 dark:text-gray-300 text-sm">
                {feature}
              </span>
            </li>
          ))}
          {limitations.map((limitation, limitationIndex) => (
            <li key={`limitation-${limitationIndex}`} className="flex items-start gap-3">
              <X className="w-5 h-5 text-gray-400 flex-shrink-0 mt-0.5" />
              <span className="text-gray-500 dark:text-gray-500 text-sm">
                {limitation}
              </span>
            </li>
          ))}
        </ul>

        <Link
          to={ctaLink}
          className={`block w-full text-center px-6 py-3 rounded-lg font-medium transition-colors ${
            recommended
              ? 'bg-blue-600 text-white hover:bg-blue-700'
              : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white hover:bg-gray-200 dark:hover:bg-gray-600'
          }`}
        >
          {ctaText}
        </Link>
      </div>
    </motion.div>
  );
};

export default PricingCard;