import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Check, X, HelpCircle, ArrowRight } from 'lucide-react';
import SEO from '../../../components/common/SEO';

interface PricingPlan {
  name: string;
  price: {
    monthly: number;
    annual: number;
  };
  description: string;
  features: string[];
  limitations?: string[];
  recommended?: boolean;
  cta: string;
}

const PricingPage: React.FC = () => {
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'annual'>('monthly');

  const plans: PricingPlan[] = [
    {
      name: 'Starter',
      price: {
        monthly: 29,
        annual: 24
      },
      description: 'Perfect for freelancers and small agencies',
      features: [
        'Up to 5 Drupal sites',
        'Real-time security monitoring',
        'Module update tracking',
        'Email alerts',
        'Basic security reports',
        'Community support'
      ],
      limitations: [
        'No API access',
        'No custom integrations',
        'No priority support'
      ],
      cta: 'Start Free Trial'
    },
    {
      name: 'Professional',
      price: {
        monthly: 99,
        annual: 83
      },
      description: 'Ideal for growing agencies and teams',
      features: [
        'Up to 50 Drupal sites',
        'Everything in Starter',
        'API access',
        'Slack & Teams integration',
        'Custom webhooks',
        'Advanced reporting',
        'Priority email support',
        'Team collaboration tools'
      ],
      recommended: true,
      cta: 'Start Free Trial'
    },
    {
      name: 'Enterprise',
      price: {
        monthly: 0,
        annual: 0
      },
      description: 'For large organizations with custom needs',
      features: [
        'Unlimited Drupal sites',
        'Everything in Professional',
        'Custom security rules',
        'White-label reports',
        'SLA guarantee',
        'Dedicated account manager',
        'Custom integrations',
        'On-premise deployment option',
        'Priority phone support'
      ],
      cta: 'Contact Sales'
    }
  ];

  const faqs = [
    {
      question: 'Can I change plans later?',
      answer: 'Yes, you can upgrade or downgrade your plan at any time. Changes take effect at the start of your next billing cycle.'
    },
    {
      question: 'What happens if I exceed my site limit?',
      answer: 'We\'ll notify you when you\'re approaching your limit. You can either upgrade your plan or remove sites to stay within your limit.'
    },
    {
      question: 'Do you offer discounts for nonprofits?',
      answer: 'Yes, we offer a 20% discount for registered nonprofit organizations. Contact our sales team with your nonprofit documentation.'
    },
    {
      question: 'Is there a setup fee?',
      answer: 'No, there are no setup fees for any of our plans. You only pay the monthly or annual subscription fee.'
    },
    {
      question: 'What payment methods do you accept?',
      answer: 'We accept all major credit cards, PayPal, and wire transfers for annual Enterprise plans.'
    },
    {
      question: 'Can I cancel anytime?',
      answer: 'Yes, you can cancel your subscription at any time. Your service will continue until the end of your current billing period.'
    }
  ];

  const calculatePrice = (plan: PricingPlan) => {
    if (plan.price.monthly === 0) return 'Custom';
    const price = billingCycle === 'monthly' ? plan.price.monthly : plan.price.annual;
    return `$${price}`;
  };

  const calculateSavings = (plan: PricingPlan) => {
    if (plan.price.monthly === 0) return null;
    const monthlyCost = plan.price.monthly * 12;
    const annualCost = plan.price.annual * 12;
    const savings = monthlyCost - annualCost;
    return savings > 0 ? Math.round((savings / monthlyCost) * 100) : 0;
  };

  return (
    <>
      <SEO
        title="Pricing - Sentinel Drupal Security Monitoring"
        description="Simple, transparent pricing for Drupal security monitoring. Choose from Starter, Professional, or Enterprise plans. 14-day free trial on all plans."
        canonicalUrl="/pricing"
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
              Simple, Transparent Pricing
            </motion.h1>
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
              className="text-xl text-gray-600 dark:text-gray-400 mb-8"
            >
              Choose the plan that fits your needs. All plans include a 14-day free trial.
            </motion.p>

            {/* Billing Toggle */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="inline-flex items-center bg-gray-100 dark:bg-gray-700 rounded-lg p-1"
            >
              <button
                onClick={() => setBillingCycle('monthly')}
                className={`px-4 py-2 rounded-md transition-colors ${
                  billingCycle === 'monthly'
                    ? 'bg-white dark:bg-gray-600 text-gray-900 dark:text-white shadow-sm'
                    : 'text-gray-600 dark:text-gray-400'
                }`}
              >
                Monthly
              </button>
              <button
                onClick={() => setBillingCycle('annual')}
                className={`px-4 py-2 rounded-md transition-colors ${
                  billingCycle === 'annual'
                    ? 'bg-white dark:bg-gray-600 text-gray-900 dark:text-white shadow-sm'
                    : 'text-gray-600 dark:text-gray-400'
                }`}
              >
                Annual
                <span className="ml-1 text-xs text-green-600 dark:text-green-400">Save 20%</span>
              </button>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Pricing Cards */}
      <section className="py-20">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {plans.map((plan, index) => {
              const savings = calculateSavings(plan);
              return (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                  className={`relative bg-white dark:bg-gray-800 rounded-xl shadow-sm hover:shadow-lg transition-shadow ${
                    plan.recommended ? 'ring-2 ring-blue-600' : ''
                  }`}
                >
                  {plan.recommended && (
                    <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                      <span className="bg-blue-600 text-white px-3 py-1 rounded-full text-sm font-medium">
                        Recommended
                      </span>
                    </div>
                  )}

                  <div className="p-8">
                    <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                      {plan.name}
                    </h3>
                    <p className="text-gray-600 dark:text-gray-400 mb-6">
                      {plan.description}
                    </p>

                    <div className="mb-6">
                      <span className="text-4xl font-bold text-gray-900 dark:text-white">
                        {calculatePrice(plan)}
                      </span>
                      {plan.price.monthly > 0 && (
                        <>
                          <span className="text-gray-600 dark:text-gray-400 ml-2">
                            per month
                          </span>
                          {billingCycle === 'annual' && savings && savings > 0 && (
                            <div className="text-sm text-green-600 dark:text-green-400 mt-1">
                              Save {savings}% with annual billing
                            </div>
                          )}
                        </>
                      )}
                    </div>

                    <ul className="space-y-3 mb-8">
                      {plan.features.map((feature, featureIndex) => (
                        <li key={featureIndex} className="flex items-start gap-3">
                          <Check className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                          <span className="text-gray-700 dark:text-gray-300 text-sm">
                            {feature}
                          </span>
                        </li>
                      ))}
                      {plan.limitations?.map((limitation, limitationIndex) => (
                        <li key={limitationIndex} className="flex items-start gap-3">
                          <X className="w-5 h-5 text-gray-400 flex-shrink-0 mt-0.5" />
                          <span className="text-gray-500 dark:text-gray-500 text-sm">
                            {limitation}
                          </span>
                        </li>
                      ))}
                    </ul>

                    <a
                      href={plan.price.monthly === 0 ? '/contact' : '/register'}
                      className={`block w-full text-center px-6 py-3 rounded-lg font-medium transition-colors ${
                        plan.recommended
                          ? 'bg-blue-600 text-white hover:bg-blue-700'
                          : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white hover:bg-gray-200 dark:hover:bg-gray-600'
                      }`}
                    >
                      {plan.cta}
                    </a>
                  </div>
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="py-20 bg-white dark:bg-gray-800">
        <div className="container mx-auto px-4">
          <div className="max-w-3xl mx-auto">
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white text-center mb-12">
              Frequently Asked Questions
            </h2>

            <div className="space-y-6">
              {faqs.map((faq, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                  className="bg-gray-50 dark:bg-gray-700 rounded-lg p-6"
                >
                  <div className="flex items-start gap-3">
                    <HelpCircle className="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
                    <div>
                      <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
                        {faq.question}
                      </h3>
                      <p className="text-gray-600 dark:text-gray-400">
                        {faq.answer}
                      </p>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>

            <div className="text-center mt-12">
              <p className="text-gray-600 dark:text-gray-400 mb-4">
                Still have questions?
              </p>
              <a
                href="/contact"
                className="inline-flex items-center gap-2 text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 font-medium"
              >
                Contact our sales team
                <ArrowRight className="w-4 h-4" />
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-blue-600 dark:bg-blue-700">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">
            Start Your 14-Day Free Trial
          </h2>
          <p className="text-xl text-blue-100 mb-8 max-w-2xl mx-auto">
            No credit card required. Get full access to all features.
          </p>
          <a
            href="/register"
            className="inline-flex items-center gap-2 px-8 py-3 bg-white text-blue-600 rounded-lg hover:bg-gray-100 transition-colors font-medium"
          >
            Get Started Now
            <ArrowRight className="w-4 h-4" />
          </a>
        </div>
      </section>
    </div>
    </>
  );
};

export default PricingPage;