import React from 'react';
import { motion } from 'framer-motion';
import { Star, Quote } from 'lucide-react';

interface TestimonialProps {
  quote: string;
  author: string;
  role: string;
  company?: string;
  avatar?: string;
  rating?: number;
  featured?: boolean;
  delay?: number;
  className?: string;
}

export const Testimonial: React.FC<TestimonialProps> = ({
  quote,
  author,
  role,
  company,
  avatar,
  rating = 5,
  featured = false,
  delay = 0,
  className = '',
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay, ease: 'easeOut' }}
      whileHover={{ y: -5 }}
      className={`
        relative bg-white dark:bg-neutral-800 rounded-xl p-6 lg:p-8
        ${featured ? 'ring-2 ring-primary-500 shadow-xl' : 'border border-neutral-200 dark:border-neutral-700 shadow-sm'}
        hover:shadow-xl transition-all duration-300
        ${className}
      `}
    >
      {/* Quote Icon */}
      <Quote className="absolute top-6 left-6 w-8 h-8 text-primary-200 dark:text-primary-800 opacity-50" />

      {/* Rating */}
      {rating > 0 && (
        <div className="flex items-center gap-1 mb-4">
          {[...Array(5)].map((_, index) => (
            <Star
              key={index}
              className={`w-4 h-4 ${
                index < rating
                  ? 'text-warning-400 fill-current'
                  : 'text-neutral-300 dark:text-neutral-600'
              }`}
            />
          ))}
        </div>
      )}

      {/* Quote */}
      <blockquote className="text-neutral-700 dark:text-neutral-300 leading-relaxed mb-6 relative z-10">
        "{quote}"
      </blockquote>

      {/* Author Info */}
      <div className="flex items-center gap-4">
        {/* Avatar */}
        {avatar ? (
          <img
            src={avatar}
            alt={author}
            className="w-12 h-12 rounded-full object-cover"
          />
        ) : (
          <div className="w-12 h-12 rounded-full bg-gradient-to-br from-primary-400 to-secondary-400 flex items-center justify-center text-white font-semibold">
            {author.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)}
          </div>
        )}

        {/* Author Details */}
        <div>
          <div className="font-semibold text-neutral-900 dark:text-white">
            {author}
          </div>
          <div className="text-sm text-neutral-600 dark:text-neutral-400">
            {role}
            {company && <span> at {company}</span>}
          </div>
        </div>
      </div>

      {/* Featured Badge */}
      {featured && (
        <div className="absolute -top-3 -right-3 bg-primary-500 text-white text-xs font-semibold px-3 py-1 rounded-full">
          Featured
        </div>
      )}
    </motion.div>
  );
};

interface TestimonialSectionProps {
  testimonials: Array<Omit<TestimonialProps, 'delay'>>;
  title?: string;
  subtitle?: string;
  columns?: 1 | 2 | 3;
  className?: string;
}

export const TestimonialSection: React.FC<TestimonialSectionProps> = ({
  testimonials,
  title = "What Our Customers Say",
  subtitle = "Trusted by teams around the world",
  columns = 3,
  className = '',
}) => {
  const gridCols = {
    1: 'grid-cols-1',
    2: 'grid-cols-1 md:grid-cols-2',
    3: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
  };

  return (
    <section className={`py-16 lg:py-24 ${className}`}>
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-12">
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-3xl sm:text-4xl font-bold text-neutral-900 dark:text-white mb-4"
          >
            {title}
          </motion.h2>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="text-lg text-neutral-600 dark:text-neutral-300 max-w-2xl mx-auto"
          >
            {subtitle}
          </motion.p>
        </div>

        {/* Testimonials Grid */}
        <div className={`grid ${gridCols[columns]} gap-6 lg:gap-8`}>
          {testimonials.map((testimonial, index) => (
            <Testimonial
              key={index}
              {...testimonial}
              delay={0.1 * (index % 3)}
            />
          ))}
        </div>

        {/* Trust Logos */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="mt-16 text-center"
        >
          <p className="text-sm text-neutral-600 dark:text-neutral-400 mb-8">
            Trusted by leading companies worldwide
          </p>
          <div className="flex flex-wrap justify-center items-center gap-8 md:gap-12 opacity-60">
            {/* Placeholder for company logos */}
            {['Company 1', 'Company 2', 'Company 3', 'Company 4', 'Company 5'].map((company, index) => (
              <div
                key={index}
                className="w-32 h-8 bg-neutral-300 dark:bg-neutral-600 rounded"
              />
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  );
};