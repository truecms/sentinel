import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  Shield, 
  Mail, 
  Phone, 
  MapPin, 
  Facebook, 
  Twitter, 
  Linkedin, 
  Github,
  ArrowRight,
  Heart
} from 'lucide-react';
import { Button } from '../../common/Button';

interface FooterLink {
  label: string;
  href: string;
}

interface FooterSection {
  title: string;
  links: FooterLink[];
}

const footerSections: FooterSection[] = [
  {
    title: 'Product',
    links: [
      { label: 'Features', href: '/features' },
      { label: 'Pricing', href: '/pricing' },
      { label: 'Security', href: '/security' },
      { label: 'Roadmap', href: '/roadmap' },
      { label: 'Changelog', href: '/changelog' },
    ],
  },
  {
    title: 'Resources',
    links: [
      { label: 'Documentation', href: '/docs' },
      { label: 'API Reference', href: '/api' },
      { label: 'Blog', href: '/blog' },
      { label: 'Support', href: '/support' },
      { label: 'Status', href: '/status' },
    ],
  },
  {
    title: 'Company',
    links: [
      { label: 'About', href: '/about' },
      { label: 'Careers', href: '/careers' },
      { label: 'Contact', href: '/contact' },
      { label: 'Partners', href: '/partners' },
      { label: 'Press', href: '/press' },
    ],
  },
  {
    title: 'Legal',
    links: [
      { label: 'Privacy Policy', href: '/privacy' },
      { label: 'Terms of Service', href: '/terms' },
      { label: 'Cookie Policy', href: '/cookies' },
      { label: 'GDPR', href: '/gdpr' },
      { label: 'License', href: '/license' },
    ],
  },
];

const socialLinks = [
  { icon: Facebook, href: 'https://facebook.com', label: 'Facebook' },
  { icon: Twitter, href: 'https://twitter.com', label: 'Twitter' },
  { icon: Linkedin, href: 'https://linkedin.com', label: 'LinkedIn' },
  { icon: Github, href: 'https://github.com', label: 'GitHub' },
];

export const PublicFooter: React.FC = () => {
  const [email, setEmail] = useState('');
  const [subscribed, setSubscribed] = useState(false);
  const [subscribing, setSubscribing] = useState(false);

  const handleSubscribe = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) return;

    setSubscribing(true);
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1500));
    setSubscribed(true);
    setSubscribing(false);
    setEmail('');
    
    // Reset after 5 seconds
    setTimeout(() => setSubscribed(false), 5000);
  };

  return (
    <footer className="bg-neutral-50 dark:bg-neutral-900 border-t border-neutral-200 dark:border-neutral-800">
      {/* Newsletter Section */}
      <div className="bg-primary-600 dark:bg-primary-700">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="max-w-4xl mx-auto text-center">
            <h3 className="text-2xl font-bold text-white mb-4">
              Stay Updated with Security Alerts
            </h3>
            <p className="text-primary-100 mb-6">
              Get the latest security updates and best practices delivered to your inbox.
            </p>
            <form onSubmit={handleSubscribe} className="max-w-md mx-auto">
              <div className="flex flex-col sm:flex-row gap-3">
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Enter your email"
                  className="flex-1 px-4 py-3 rounded-lg bg-white/10 backdrop-blur-sm border border-white/20 text-white placeholder-white/60 focus:outline-none focus:ring-2 focus:ring-white/30"
                  required
                />
                <Button
                  type="submit"
                  variant="secondary"
                  size="lg"
                  isLoading={subscribing}
                  rightIcon={!subscribing && <ArrowRight className="w-4 h-4" />}
                >
                  {subscribed ? 'Subscribed!' : 'Subscribe'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      </div>

      {/* Main Footer Content */}
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-12 lg:py-16">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-8 lg:gap-12">
          {/* Company Info */}
          <div className="lg:col-span-2">
            <Link to="/" className="flex items-center space-x-3 mb-6">
              <Shield className="h-8 w-8 text-primary-600 dark:text-primary-400" />
              <span className="text-xl font-bold text-neutral-900 dark:text-white">
                Sentinel
              </span>
            </Link>
            <p className="text-neutral-600 dark:text-neutral-300 mb-6">
              Enterprise-grade security monitoring for Drupal websites. Protect your digital assets with real-time threat detection and automated vulnerability scanning.
            </p>
            
            {/* Contact Info */}
            <div className="space-y-3 text-sm">
              <a
                href="mailto:hello@sentinel.io"
                className="flex items-center text-neutral-600 hover:text-primary-600 dark:text-neutral-400 dark:hover:text-primary-400 transition-colors"
              >
                <Mail className="w-4 h-4 mr-3" />
                hello@sentinel.io
              </a>
              <a
                href="tel:+1234567890"
                className="flex items-center text-neutral-600 hover:text-primary-600 dark:text-neutral-400 dark:hover:text-primary-400 transition-colors"
              >
                <Phone className="w-4 h-4 mr-3" />
                +1 (234) 567-890
              </a>
              <div className="flex items-start text-neutral-600 dark:text-neutral-400">
                <MapPin className="w-4 h-4 mr-3 mt-0.5" />
                <span>
                  123 Security Lane<br />
                  San Francisco, CA 94105
                </span>
              </div>
            </div>
          </div>

          {/* Footer Links */}
          {footerSections.map((section) => (
            <div key={section.title}>
              <h4 className="font-semibold text-neutral-900 dark:text-white mb-4">
                {section.title}
              </h4>
              <ul className="space-y-3">
                {section.links.map((link) => (
                  <li key={link.label}>
                    <Link
                      to={link.href}
                      className="text-sm text-neutral-600 hover:text-primary-600 dark:text-neutral-400 dark:hover:text-primary-400 transition-colors"
                    >
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Bottom Bar */}
        <div className="mt-12 pt-8 border-t border-neutral-200 dark:border-neutral-700">
          <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
            {/* Copyright */}
            <div className="text-sm text-neutral-600 dark:text-neutral-400 text-center md:text-left">
              © {new Date().getFullYear()} Sentinel. All rights reserved. Made with{' '}
              <Heart className="inline-block w-4 h-4 text-danger-500 fill-current" /> by the Sentinel team.
            </div>

            {/* Social Links */}
            <div className="flex items-center space-x-4">
              {socialLinks.map((social) => {
                const Icon = social.icon;
                return (
                  <motion.a
                    key={social.label}
                    href={social.href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="p-2 text-neutral-600 hover:text-primary-600 dark:text-neutral-400 dark:hover:text-primary-400 transition-colors"
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.95 }}
                    aria-label={social.label}
                  >
                    <Icon className="w-5 h-5" />
                  </motion.a>
                );
              })}
            </div>
          </div>
        </div>
      </div>

      {/* Trust Badges */}
      <div className="bg-neutral-100 dark:bg-neutral-800 py-6">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-wrap justify-center items-center gap-8 opacity-60">
            <img
              src="/assets/badges/soc2.svg"
              alt="SOC 2 Compliant"
              className="h-8 grayscale hover:grayscale-0 transition-all"
            />
            <img
              src="/assets/badges/gdpr.svg"
              alt="GDPR Compliant"
              className="h-8 grayscale hover:grayscale-0 transition-all"
            />
            <img
              src="/assets/badges/iso27001.svg"
              alt="ISO 27001 Certified"
              className="h-8 grayscale hover:grayscale-0 transition-all"
            />
            <img
              src="/assets/badges/pci.svg"
              alt="PCI DSS Compliant"
              className="h-8 grayscale hover:grayscale-0 transition-all"
            />
          </div>
        </div>
      </div>
    </footer>
  );
};