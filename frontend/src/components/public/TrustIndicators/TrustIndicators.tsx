import React from 'react';
import { motion } from 'framer-motion';
import { Shield, Award, Users, Clock, CheckCircle, TrendingUp } from 'lucide-react';

interface Stat {
  label: string;
  value: string;
  icon?: React.ReactNode;
  suffix?: string;
  description?: string;
}

interface Badge {
  name: string;
  image?: string;
  icon?: React.ReactNode;
  description?: string;
}

interface TrustIndicatorsProps {
  stats?: Stat[];
  badges?: Badge[];
  title?: string;
  subtitle?: string;
  variant?: 'stats' | 'badges' | 'combined';
  className?: string;
}

const defaultStats: Stat[] = [
  {
    label: 'Uptime SLA',
    value: '99.9',
    suffix: '%',
    icon: <Clock className="w-6 h-6" />,
    description: 'Guaranteed uptime',
  },
  {
    label: 'Sites Protected',
    value: '10K',
    suffix: '+',
    icon: <Shield className="w-6 h-6" />,
    description: 'And growing',
  },
  {
    label: 'Security Threats Blocked',
    value: '2.5M',
    suffix: '+',
    icon: <TrendingUp className="w-6 h-6" />,
    description: 'This month',
  },
  {
    label: 'Happy Customers',
    value: '500',
    suffix: '+',
    icon: <Users className="w-6 h-6" />,
    description: 'Worldwide',
  },
];

const defaultBadges: Badge[] = [
  {
    name: 'SOC 2 Type II',
    icon: <Award className="w-8 h-8" />,
    description: 'Certified',
  },
  {
    name: 'ISO 27001',
    icon: <CheckCircle className="w-8 h-8" />,
    description: 'Certified',
  },
  {
    name: 'GDPR',
    icon: <Shield className="w-8 h-8" />,
    description: 'Compliant',
  },
  {
    name: 'PCI DSS',
    icon: <Award className="w-8 h-8" />,
    description: 'Level 1',
  },
];

export const TrustIndicators: React.FC<TrustIndicatorsProps> = ({
  stats = defaultStats,
  badges = defaultBadges,
  title = "Trusted by Leading Organizations",
  subtitle = "Our commitment to security and reliability",
  variant = 'combined',
  className = '',
}) => {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.6,
        ease: 'easeOut',
      },
    },
  };

  const renderStats = () => (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="grid grid-cols-2 md:grid-cols-4 gap-8"
    >
      {stats.map((stat, index) => (
        <motion.div
          key={index}
          variants={itemVariants}
          className="text-center"
        >
          {stat.icon && (
            <div className="inline-flex items-center justify-center w-12 h-12 rounded-lg bg-primary-100 text-primary-600 dark:bg-primary-900 dark:text-primary-400 mb-4">
              {stat.icon}
            </div>
          )}
          <div className="text-3xl sm:text-4xl font-bold text-neutral-900 dark:text-white">
            {stat.value}
            {stat.suffix && (
              <span className="text-2xl sm:text-3xl">{stat.suffix}</span>
            )}
          </div>
          <div className="text-sm font-medium text-neutral-700 dark:text-neutral-300 mt-1">
            {stat.label}
          </div>
          {stat.description && (
            <div className="text-xs text-neutral-500 dark:text-neutral-400 mt-1">
              {stat.description}
            </div>
          )}
        </motion.div>
      ))}
    </motion.div>
  );

  const renderBadges = () => (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="flex flex-wrap justify-center items-center gap-8 md:gap-12"
    >
      {badges.map((badge, index) => (
        <motion.div
          key={index}
          variants={itemVariants}
          whileHover={{ scale: 1.05 }}
          className="text-center"
        >
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-neutral-100 dark:bg-neutral-800 mb-3 group-hover:bg-primary-100 dark:group-hover:bg-primary-900 transition-colors">
            {badge.image ? (
              <img
                src={badge.image}
                alt={badge.name}
                className="w-12 h-12 object-contain filter grayscale group-hover:grayscale-0 transition-all"
              />
            ) : (
              <div className="text-neutral-600 dark:text-neutral-400 group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">
                {badge.icon}
              </div>
            )}
          </div>
          <div className="text-sm font-medium text-neutral-700 dark:text-neutral-300">
            {badge.name}
          </div>
          {badge.description && (
            <div className="text-xs text-neutral-500 dark:text-neutral-400">
              {badge.description}
            </div>
          )}
        </motion.div>
      ))}
    </motion.div>
  );

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

        {/* Content based on variant */}
        {variant === 'stats' && renderStats()}
        {variant === 'badges' && renderBadges()}
        {variant === 'combined' && (
          <div className="space-y-16">
            {renderStats()}
            <div className="border-t border-neutral-200 dark:border-neutral-700" />
            {renderBadges()}
          </div>
        )}
      </div>

      {/* Background decoration */}
      <div className="absolute inset-0 -z-10 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-primary-200 dark:bg-primary-900 rounded-full opacity-20 blur-3xl" />
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-secondary-200 dark:bg-secondary-900 rounded-full opacity-20 blur-3xl" />
      </div>
    </section>
  );
};