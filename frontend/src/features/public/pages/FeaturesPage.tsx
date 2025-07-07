import React from 'react';
import { motion } from 'framer-motion';
import { 
  Shield, Activity, Bell, BarChart3, Lock, Cloud, 
  Zap, Users, Code, Database, Globe, Clock,
  CheckCircle, ArrowRight
} from 'lucide-react';
import SEO from '../../../components/common/SEO';

interface FeatureCategory {
  title: string;
  description: string;
  features: Feature[];
}

interface Feature {
  icon: React.ReactNode;
  title: string;
  description: string;
}

const FeaturesPage: React.FC = () => {
  const featureCategories: FeatureCategory[] = [
    {
      title: 'Security Monitoring',
      description: 'Comprehensive security features to keep your Drupal sites protected.',
      features: [
        {
          icon: <Shield className="w-5 h-5" />,
          title: 'Vulnerability Detection',
          description: 'Automatic scanning for known security vulnerabilities in Drupal core and modules.'
        },
        {
          icon: <Lock className="w-5 h-5" />,
          title: 'Security Advisories',
          description: 'Real-time updates on security advisories from Drupal.org and other sources.'
        },
        {
          icon: <Activity className="w-5 h-5" />,
          title: 'Threat Analysis',
          description: 'Advanced threat detection and analysis to identify potential security risks.'
        },
        {
          icon: <Bell className="w-5 h-5" />,
          title: 'Instant Alerts',
          description: 'Get notified immediately when security issues are detected on your sites.'
        }
      ]
    },
    {
      title: 'Module Management',
      description: 'Stay on top of module updates and dependencies with powerful management tools.',
      features: [
        {
          icon: <Code className="w-5 h-5" />,
          title: 'Version Tracking',
          description: 'Track all module versions across your sites and identify outdated components.'
        },
        {
          icon: <Database className="w-5 h-5" />,
          title: 'Update Management',
          description: 'Centralized dashboard to manage and schedule module updates across sites.'
        },
        {
          icon: <Zap className="w-5 h-5" />,
          title: 'Dependency Analysis',
          description: 'Understand module dependencies and potential conflicts before updating.'
        },
        {
          icon: <Globe className="w-5 h-5" />,
          title: 'Patch Detection',
          description: 'Identify sites using patched modules and track patch compatibility.'
        }
      ]
    },
    {
      title: 'Reporting & Analytics',
      description: 'Gain insights into your sites\' security posture with detailed reporting.',
      features: [
        {
          icon: <BarChart3 className="w-5 h-5" />,
          title: 'Security Reports',
          description: 'Comprehensive security reports for individual sites or your entire portfolio.'
        },
        {
          icon: <Clock className="w-5 h-5" />,
          title: 'Historical Data',
          description: 'Track security trends over time and measure improvement metrics.'
        },
        {
          icon: <Users className="w-5 h-5" />,
          title: 'Team Dashboards',
          description: 'Customizable dashboards for different team members and stakeholders.'
        },
        {
          icon: <Cloud className="w-5 h-5" />,
          title: 'Export Options',
          description: 'Export reports in multiple formats for compliance and documentation.'
        }
      ]
    }
  ];

  const comparisonData = [
    { feature: 'Real-time Security Monitoring', starter: true, pro: true, enterprise: true },
    { feature: 'Module Update Tracking', starter: true, pro: true, enterprise: true },
    { feature: 'Email Alerts', starter: true, pro: true, enterprise: true },
    { feature: 'Number of Sites', starter: 'Up to 5', pro: 'Up to 50', enterprise: 'Unlimited' },
    { feature: 'API Access', starter: false, pro: true, enterprise: true },
    { feature: 'Slack/Teams Integration', starter: false, pro: true, enterprise: true },
    { feature: 'Custom Webhooks', starter: false, pro: true, enterprise: true },
    { feature: 'Priority Support', starter: false, pro: true, enterprise: true },
    { feature: 'Custom Security Rules', starter: false, pro: false, enterprise: true },
    { feature: 'White-label Reports', starter: false, pro: false, enterprise: true },
    { feature: 'SLA Guarantee', starter: false, pro: false, enterprise: true },
    { feature: 'Dedicated Account Manager', starter: false, pro: false, enterprise: true }
  ];

  return (
    <>
      <SEO
        title="Features - Sentinel Drupal Security Monitoring"
        description="Explore Sentinel's comprehensive features: real-time security monitoring, vulnerability detection, module management, and detailed reporting for Drupal sites."
        canonicalUrl="/features"
      />
      <div className="bg-gray-50 dark:bg-gray-900">
      {/* Hero Section */}
      <section className="py-20 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="container mx-auto px-4">
          <div className="text-center max-w-3xl mx-auto">
            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="text-4xl md:text-5xl font-bold text-gray-900 dark:text-white mb-6"
            >
              Powerful Features for Drupal Security
            </motion.h1>
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
              className="text-xl text-gray-600 dark:text-gray-400"
            >
              Everything you need to monitor, protect, and maintain your Drupal sites 
              in one comprehensive platform.
            </motion.p>
          </div>
        </div>
      </section>

      {/* Feature Categories */}
      {featureCategories.map((category, categoryIndex) => (
        <section key={categoryIndex} className={categoryIndex % 2 === 0 ? 'py-20' : 'py-20 bg-white dark:bg-gray-800'}>
          <div className="container mx-auto px-4">
            <div className="text-center mb-12">
              <motion.h2
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
                className="text-3xl font-bold text-gray-900 dark:text-white mb-4"
              >
                {category.title}
              </motion.h2>
              <motion.p
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.1 }}
                className="text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto"
              >
                {category.description}
              </motion.p>
            </div>

            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
              {category.features.map((feature, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                  className="bg-gray-50 dark:bg-gray-700 p-6 rounded-lg"
                >
                  <div className="w-10 h-10 bg-blue-100 dark:bg-blue-900 text-blue-600 dark:text-blue-400 rounded-lg flex items-center justify-center mb-4">
                    {feature.icon}
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                    {feature.title}
                  </h3>
                  <p className="text-gray-600 dark:text-gray-400 text-sm">
                    {feature.description}
                  </p>
                </motion.div>
              ))}
            </div>
          </div>
        </section>
      ))}

      {/* Feature Comparison Table */}
      <section className="py-20 bg-white dark:bg-gray-800">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
              Compare Plans
            </h2>
            <p className="text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
              Choose the plan that best fits your needs. All plans include our core security features.
            </p>
          </div>

          <div className="max-w-5xl mx-auto overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200 dark:border-gray-700">
                  <th className="text-left py-4 px-4 text-gray-900 dark:text-white font-semibold">
                    Features
                  </th>
                  <th className="text-center py-4 px-4 text-gray-900 dark:text-white font-semibold">
                    Starter
                  </th>
                  <th className="text-center py-4 px-4 text-gray-900 dark:text-white font-semibold">
                    Professional
                  </th>
                  <th className="text-center py-4 px-4 text-gray-900 dark:text-white font-semibold">
                    Enterprise
                  </th>
                </tr>
              </thead>
              <tbody>
                {comparisonData.map((row, index) => (
                  <tr 
                    key={index} 
                    className="border-b border-gray-100 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700"
                  >
                    <td className="py-4 px-4 text-gray-700 dark:text-gray-300">
                      {row.feature}
                    </td>
                    <td className="text-center py-4 px-4">
                      {typeof row.starter === 'boolean' ? (
                        row.starter ? (
                          <CheckCircle className="w-5 h-5 text-green-500 mx-auto" />
                        ) : (
                          <span className="text-gray-400">-</span>
                        )
                      ) : (
                        <span className="text-gray-700 dark:text-gray-300">{row.starter}</span>
                      )}
                    </td>
                    <td className="text-center py-4 px-4">
                      {typeof row.pro === 'boolean' ? (
                        row.pro ? (
                          <CheckCircle className="w-5 h-5 text-green-500 mx-auto" />
                        ) : (
                          <span className="text-gray-400">-</span>
                        )
                      ) : (
                        <span className="text-gray-700 dark:text-gray-300">{row.pro}</span>
                      )}
                    </td>
                    <td className="text-center py-4 px-4">
                      {typeof row.enterprise === 'boolean' ? (
                        row.enterprise ? (
                          <CheckCircle className="w-5 h-5 text-green-500 mx-auto" />
                        ) : (
                          <span className="text-gray-400">-</span>
                        )
                      ) : (
                        <span className="text-gray-700 dark:text-gray-300">{row.enterprise}</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="text-center mt-8">
            <a
              href="/pricing"
              className="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              View Pricing Details
              <ArrowRight className="w-4 h-4" />
            </a>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-blue-600 dark:bg-blue-700">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">
            Ready to Get Started?
          </h2>
          <p className="text-xl text-blue-100 mb-8 max-w-2xl mx-auto">
            Start monitoring your Drupal sites today with our 14-day free trial.
          </p>
          <a
            href="/register"
            className="inline-flex items-center gap-2 px-8 py-3 bg-white text-blue-600 rounded-lg hover:bg-gray-100 transition-colors font-medium"
          >
            Start Free Trial
            <ArrowRight className="w-4 h-4" />
          </a>
        </div>
      </section>
    </div>
    </>
  );
};

export default FeaturesPage;