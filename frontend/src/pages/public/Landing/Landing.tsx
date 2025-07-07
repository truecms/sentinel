import React from 'react';
import { 
  Shield, 
  Lock, 
  AlertCircle, 
  TrendingUp, 
  Zap, 
  BarChart,
  CheckCircle
} from 'lucide-react';
import {
  PublicHeader,
  PublicFooter,
  Hero,
  FeatureCard,
  PricingCard,
  FAQ,
  CTA,
  TestimonialSection,
  TrustIndicators
} from '../../../components/public';

const features = [
  {
    icon: Shield,
    title: 'Real-time Security Monitoring',
    description: 'Monitor your Drupal sites 24/7 for security vulnerabilities and threats with instant alerts.',
    features: ['Continuous scanning', 'Instant notifications', 'Threat intelligence'],
    color: 'primary' as const,
  },
  {
    icon: Lock,
    title: 'Vulnerability Detection',
    description: 'Automatically detect known vulnerabilities in Drupal core and contributed modules.',
    features: ['CVE database', 'Zero-day protection', 'Patch management'],
    color: 'secondary' as const,
  },
  {
    icon: AlertCircle,
    title: 'Smart Alerts',
    description: 'Get intelligent alerts only when it matters, reducing alert fatigue and false positives.',
    features: ['Priority-based alerts', 'Custom thresholds', 'Multi-channel delivery'],
    color: 'warning' as const,
  },
  {
    icon: TrendingUp,
    title: 'Module Update Tracking',
    description: 'Track all module updates and security patches across your entire Drupal fleet.',
    features: ['Automated tracking', 'Update recommendations', 'Compatibility checks'],
    color: 'success' as const,
  },
  {
    icon: Zap,
    title: 'Performance Monitoring',
    description: 'Monitor site performance and availability to ensure optimal user experience.',
    features: ['Uptime monitoring', 'Response time tracking', 'Performance insights'],
    color: 'info' as const,
  },
  {
    icon: BarChart,
    title: 'Compliance Reporting',
    description: 'Generate compliance reports for SOC 2, GDPR, and other security standards.',
    features: ['Automated reports', 'Audit trails', 'Export capabilities'],
    color: 'danger' as const,
  },
];

const pricingPlans = [
  {
    name: 'Starter',
    description: 'Perfect for small teams',
    price: '29',
    features: [
      'Up to 5 sites',
      'Daily security scans',
      'Email alerts',
      'Basic reporting',
      { text: 'Priority support', included: false },
      { text: 'API access', included: false },
    ],
  },
  {
    name: 'Professional',
    description: 'For growing organizations',
    price: '99',
    recommended: true,
    features: [
      'Up to 25 sites',
      'Real-time monitoring',
      'Multi-channel alerts',
      'Advanced reporting',
      'Priority support',
      'API access',
    ],
  },
  {
    name: 'Enterprise',
    description: 'For large deployments',
    price: 'Custom',
    priceUnit: '',
    features: [
      'Unlimited sites',
      'Custom monitoring rules',
      'White-label options',
      'Dedicated account manager',
      'SLA guarantee',
      'Custom integrations',
    ],
  },
];

const faqItems = [
  {
    id: '1',
    question: 'How does Sentinel monitor my Drupal sites?',
    answer: 'Sentinel uses a lightweight module installed on your Drupal sites that securely communicates with our monitoring platform. The module performs regular security scans, tracks module versions, and monitors for vulnerabilities without impacting your site performance.',
    category: 'Technical',
  },
  {
    id: '2',
    question: 'What types of security issues can Sentinel detect?',
    answer: 'Sentinel detects a wide range of security issues including outdated modules with known vulnerabilities, unauthorized file changes, suspicious user activities, configuration weaknesses, and potential security breaches. Our threat intelligence is updated continuously.',
    category: 'Features',
  },
  {
    id: '3',
    question: 'How quickly will I be notified of security issues?',
    answer: 'Critical security issues trigger instant alerts through your configured channels (email, SMS, Slack, etc.). Non-critical issues are batched and sent according to your notification preferences, typically within minutes of detection.',
    category: 'Features',
  },
  {
    id: '4',
    question: 'Can I try Sentinel before committing to a paid plan?',
    answer: 'Yes! We offer a 14-day free trial with full access to all Professional plan features. No credit card required. You can monitor up to 5 sites during the trial period.',
    category: 'Pricing',
  },
  {
    id: '5',
    question: 'Is my data secure with Sentinel?',
    answer: 'Absolutely. We use bank-level encryption for all data transmission and storage. We\'re SOC 2 Type II certified, GDPR compliant, and undergo regular security audits. Your site data is never shared with third parties.',
    category: 'Security',
  },
  {
    id: '6',
    question: 'Do you support multisite Drupal installations?',
    answer: 'Yes, Sentinel fully supports Drupal multisite installations. You can monitor all subsites from a single dashboard and set up site-specific or global monitoring rules.',
    category: 'Technical',
  },
];

const testimonials = [
  {
    quote: "Sentinel has transformed how we manage security across our Drupal portfolio. The real-time alerts have helped us prevent several potential breaches.",
    author: "Sarah Johnson",
    role: "CTO",
    company: "TechCorp Inc.",
    rating: 5,
    featured: true,
  },
  {
    quote: "The compliance reporting features alone justify the investment. We've cut our audit preparation time by 70%.",
    author: "Michael Chen",
    role: "Security Manager",
    company: "Global Media Group",
    rating: 5,
  },
  {
    quote: "Outstanding support team and a product that actually delivers on its promises. Highly recommended for any Drupal team.",
    author: "Emily Rodriguez",
    role: "DevOps Lead",
    company: "StartupXYZ",
    rating: 5,
  },
];

export const Landing: React.FC = () => {
  return (
    <div className="min-h-screen bg-white dark:bg-neutral-900">
      <PublicHeader />
      
      {/* Hero Section */}
      <Hero />

      {/* Trust Indicators */}
      <TrustIndicators variant="stats" />

      {/* Features Section */}
      <section className="py-16 lg:py-24 bg-neutral-50 dark:bg-neutral-800">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl sm:text-4xl font-bold text-neutral-900 dark:text-white mb-4">
              Comprehensive Security Features
            </h2>
            <p className="text-lg text-neutral-600 dark:text-neutral-300 max-w-2xl mx-auto">
              Everything you need to keep your Drupal sites secure and compliant
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 lg:gap-8">
            {features.map((feature, index) => (
              <FeatureCard
                key={index}
                {...feature}
                delay={index * 0.1}
              />
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-16 lg:py-24">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl sm:text-4xl font-bold text-neutral-900 dark:text-white mb-4">
              How It Works
            </h2>
            <p className="text-lg text-neutral-600 dark:text-neutral-300 max-w-2xl mx-auto">
              Get started in minutes with our simple 3-step process
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              {
                step: '1',
                title: 'Install Module',
                description: 'Install our lightweight Drupal module on your sites',
                icon: <Zap className="w-8 h-8" />,
              },
              {
                step: '2',
                title: 'Configure Monitoring',
                description: 'Set up your monitoring preferences and alert channels',
                icon: <Shield className="w-8 h-8" />,
              },
              {
                step: '3',
                title: 'Stay Protected',
                description: 'Receive real-time alerts and security insights',
                icon: <CheckCircle className="w-8 h-8" />,
              },
            ].map((item, index) => (
              <div key={index} className="text-center">
                <div className="relative inline-flex items-center justify-center w-20 h-20 mb-6">
                  <div className="absolute inset-0 bg-primary-100 dark:bg-primary-900 rounded-full animate-pulse-scale" />
                  <div className="relative z-10 flex items-center justify-center w-16 h-16 bg-primary-500 text-white rounded-full">
                    {item.icon}
                  </div>
                  <div className="absolute -top-2 -right-2 w-8 h-8 bg-secondary-500 text-white rounded-full flex items-center justify-center text-sm font-bold">
                    {item.step}
                  </div>
                </div>
                <h3 className="text-xl font-semibold text-neutral-900 dark:text-white mb-2">
                  {item.title}
                </h3>
                <p className="text-neutral-600 dark:text-neutral-300">
                  {item.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <TestimonialSection
        testimonials={testimonials}
        className="bg-neutral-50 dark:bg-neutral-800"
      />

      {/* Pricing Section */}
      <section className="py-16 lg:py-24">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl sm:text-4xl font-bold text-neutral-900 dark:text-white mb-4">
              Simple, Transparent Pricing
            </h2>
            <p className="text-lg text-neutral-600 dark:text-neutral-300 max-w-2xl mx-auto">
              Choose the plan that fits your needs. All plans include core security features.
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 lg:gap-8 max-w-5xl mx-auto">
            {pricingPlans.map((plan, index) => (
              <PricingCard
                key={index}
                {...plan}
                delay={index * 0.1}
              />
            ))}
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <FAQ
        items={faqItems}
        className="bg-neutral-50 dark:bg-neutral-800"
      />

      {/* CTA Section */}
      <CTA
        title="Ready to Secure Your Drupal Sites?"
        subtitle="Join thousands of teams who trust Sentinel to protect their digital assets"
        primaryButton={{ text: "Start Free Trial", href: "/signup" }}
        secondaryButton={{ text: "Schedule Demo", href: "/demo" }}
      />

      <PublicFooter />
    </div>
  );
};