import React from 'react';
import { NavLink } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  LayoutDashboard,
  Globe,
  Shield,
  FileText,
  Settings,
} from 'lucide-react';

interface MobileNavItem {
  label: string;
  icon: React.ElementType;
  path: string;
}

const mobileNavItems: MobileNavItem[] = [
  {
    label: 'Dashboard',
    icon: LayoutDashboard,
    path: '/dashboard',
  },
  {
    label: 'Sites',
    icon: Globe,
    path: '/sites',
  },
  {
    label: 'Modules',
    icon: Shield,
    path: '/modules',
  },
  {
    label: 'Reports',
    icon: FileText,
    path: '/reports',
  },
  {
    label: 'Settings',
    icon: Settings,
    path: '/settings',
  },
];

export const MobileNav: React.FC = () => {
  return (
    <nav className="lg:hidden fixed bottom-0 left-0 right-0 z-50 bg-white border-t border-neutral-200 dark:bg-neutral-900 dark:border-neutral-800">
      <div className="grid grid-cols-5 h-16">
        {mobileNavItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `relative flex flex-col items-center justify-center space-y-1 transition-colors ${
                isActive
                  ? 'text-primary-600 dark:text-primary-400'
                  : 'text-neutral-600 dark:text-neutral-400'
              }`
            }
          >
            {({ isActive }) => (
              <>
                <item.icon className="w-5 h-5" />
                <span className="text-xs font-medium">{item.label}</span>
                {isActive && (
                  <motion.div
                    layoutId="mobile-nav-indicator"
                    className="absolute top-0 left-0 right-0 h-0.5 bg-primary-600 dark:bg-primary-400"
                    transition={{
                      type: 'spring',
                      stiffness: 400,
                      damping: 30,
                    }}
                  />
                )}
              </>
            )}
          </NavLink>
        ))}
      </div>
    </nav>
  );
};