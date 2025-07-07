import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Shield, Activity, Bell, BarChart3, ArrowRight } from 'lucide-react';
import SEO from '../../../components/common/SEO';

const LandingPage: React.FC = () => {
  const features = [
    {
      icon: <Shield className="w-6 h-6" />,
      title: 'Security Monitoring',
      description: 'Real-time security vulnerability detection and automated alerts for your Drupal sites.'
    },
    {
      icon: <Activity className="w-6 h-6" />,
      title: 'Module Updates',
      description: 'Track module versions and get notified about critical updates and patches.'
    },
    {
      icon: <Bell className="w-6 h-6" />,
      title: 'Smart Alerts',
      description: 'Customizable notifications via email, Slack, or webhooks for critical issues.'
    },
    {
      icon: <BarChart3 className="w-6 h-6" />,
      title: 'Detailed Reports',
      description: 'Comprehensive security reports and analytics for all your Drupal sites.'
    }
  ];

  const stats = [
    { value: '10K+', label: 'Sites Monitored' },
    { value: '99.9%', label: 'Uptime' },
    { value: '24/7', label: 'Monitoring' },
    { value: '<5min', label: 'Alert Time' }
  ];

  return (
    <>
      <SEO
        title="Sentinel - Drupal Security Monitoring Platform"
        description="Monitor your Drupal sites' security with real-time vulnerability detection, automated module updates tracking, and comprehensive security reporting."
        canonicalUrl="/"
      />
      <div className="bg-gray-50 dark:bg-gray-900">
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div className="container mx-auto px-4 py-20 lg:py-32">
          <div className="text-center max-w-4xl mx-auto">
            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="text-4xl md:text-6xl font-bold text-gray-900 dark:text-white mb-6"
            >
              Monitor Your Drupal Sites' Security
            </motion.h1>
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
              className="text-xl text-gray-600 dark:text-gray-400 mb-8"
            >
              Get real-time security monitoring, automated vulnerability detection, and 
              comprehensive reporting for all your Drupal sites in one powerful dashboard.
            </motion.p>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="flex flex-col sm:flex-row gap-4 justify-center"
            >
              <Link
                to="/register"
                className="px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
              >
                Start Free Trial
              </Link>
              <Link
                to="/features"
                className="px-8 py-3 bg-white dark:bg-gray-800 text-gray-900 dark:text-white rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors font-medium border border-gray-300 dark:border-gray-700"
              >
                Learn More
              </Link>
            </motion.div>
          </div>
        </div>

        {/* Background decoration */}
        <div className="absolute inset-0 -z-10">
          <div className="absolute inset-0 bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 opacity-50" />
          <div className="absolute right-0 top-0 -translate-y-1/4 translate-x-1/4 w-96 h-96 bg-blue-500 rounded-full blur-3xl opacity-20" />
          <div className="absolute left-0 bottom-0 translate-y-1/4 -translate-x-1/4 w-96 h-96 bg-indigo-500 rounded-full blur-3xl opacity-20" />
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 bg-white dark:bg-gray-800 border-y border-gray-200 dark:border-gray-700">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                className="text-center"
              >
                <div className="text-3xl md:text-4xl font-bold text-blue-600 dark:text-blue-400 mb-2">
                  {stat.value}
                </div>
                <div className="text-gray-600 dark:text-gray-400">{stat.label}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">
              Everything You Need to Keep Your Sites Secure
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-400 max-w-3xl mx-auto">
              Comprehensive security monitoring and management tools designed specifically for Drupal sites.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm hover:shadow-md transition-shadow"
              >
                <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900 text-blue-600 dark:text-blue-400 rounded-lg flex items-center justify-center mb-4">
                  {feature.icon}
                </div>
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                  {feature.title}
                </h3>
                <p className="text-gray-600 dark:text-gray-400">
                  {feature.description}
                </p>
              </motion.div>
            ))}
          </div>

          <div className="text-center mt-12">
            <Link
              to="/features"
              className="inline-flex items-center gap-2 text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 font-medium"
            >
              View All Features
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-20 bg-white dark:bg-gray-800">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">
              How It Works
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-400 max-w-3xl mx-auto">
              Get started in minutes with our simple three-step process.
            </p>
          </div>

          <div className="max-w-4xl mx-auto">
            <div className="space-y-8">
              {[
                {
                  step: '1',
                  title: 'Connect Your Sites',
                  description: 'Install our lightweight module on your Drupal sites to enable monitoring.'
                },
                {
                  step: '2',
                  title: 'Configure Monitoring',
                  description: 'Set up security rules, alert preferences, and monitoring frequency.'
                },
                {
                  step: '3',
                  title: 'Stay Protected',
                  description: 'Receive real-time alerts and detailed reports about your sites\' security.'
                }
              ].map((item, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                  className="flex gap-4"
                >
                  <div className="flex-shrink-0 w-12 h-12 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold">
                    {item.step}
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                      {item.title}
                    </h3>
                    <p className="text-gray-600 dark:text-gray-400">
                      {item.description}
                    </p>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-blue-600 dark:bg-blue-700">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
            Ready to Secure Your Drupal Sites?
          </h2>
          <p className="text-xl text-blue-100 mb-8 max-w-2xl mx-auto">
            Join thousands of developers and agencies who trust Sentinel to keep their Drupal sites secure.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/register"
              className="px-8 py-3 bg-white text-blue-600 rounded-lg hover:bg-gray-100 transition-colors font-medium"
            >
              Start Free Trial
            </Link>
            <Link
              to="/pricing"
              className="px-8 py-3 bg-blue-700 dark:bg-blue-800 text-white rounded-lg hover:bg-blue-800 dark:hover:bg-blue-900 transition-colors font-medium"
            >
              View Pricing
            </Link>
          </div>
        </div>
      </section>
    </div>
    </>
  );
};

export default LandingPage;