import React from 'react';
import { NavLink } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  LayoutDashboard,
  Globe,
  Package,
  FileText,
  Settings,
  BarChart3,
  X,
  Building2,
} from 'lucide-react';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
  isCollapsed?: boolean;
  onToggleCollapse?: () => void;
  sitesCount?: number;
  modulesCount?: number;
}

interface NavItem {
  label: string;
  icon: React.ElementType;
  path: string;
  badge?: string | number;
  badgeType?: 'info' | 'warning' | 'danger' | 'success';
}

const getNavItems = (sitesCount?: number, modulesCount?: number): NavItem[] => [
  {
    label: 'Dashboard',
    icon: LayoutDashboard,
    path: '/app/dashboard',
  },
  {
    label: 'Organizations',
    icon: Building2,
    path: '/app/organizations',
  },
  {
    label: 'Sites',
    icon: Globe,
    path: '/app/sites',
    badge: sitesCount !== undefined ? sitesCount : undefined,
    badgeType: 'info',
  },
  {
    label: 'Modules',
    icon: Package,
    path: '/app/modules',
    badge: modulesCount !== undefined ? modulesCount : undefined,
    badgeType: 'warning',
  },
  {
    label: 'Reports',
    icon: FileText,
    path: '/app/reports',
  },
  {
    label: 'Settings',
    icon: Settings,
    path: '/app/settings',
  },
];

const getBadgeClasses = (type?: string) => {
  switch (type) {
    case 'info':
      return 'bg-info-100 text-info-700 dark:bg-info-900 dark:text-info-200';
    case 'warning':
      return 'bg-warning-100 text-warning-700 dark:bg-warning-900 dark:text-warning-200';
    case 'danger':
      return 'bg-danger-100 text-danger-700 dark:bg-danger-900 dark:text-danger-200';
    case 'success':
      return 'bg-success-100 text-success-700 dark:bg-success-900 dark:text-success-200';
    default:
      return 'bg-neutral-100 text-neutral-700 dark:bg-neutral-800 dark:text-neutral-200';
  }
};

export const Sidebar: React.FC<SidebarProps> = ({
  isOpen,
  onClose,
  isCollapsed = false,
  onToggleCollapse,
  sitesCount,
  modulesCount,
}) => {
  const navItems = getNavItems(sitesCount, modulesCount);
  const sidebarVariants = {
    open: { x: 0 },
    closed: { x: '-100%' },
  };

  const contentVariants = {
    expanded: { opacity: 1, x: 0 },
    collapsed: { opacity: 0, x: -20 },
  };

  return (
    <>
      {/* Mobile Overlay */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="lg:hidden fixed inset-0 bg-black bg-opacity-50 z-40"
          />
        )}
      </AnimatePresence>

      {/* Sidebar */}
      <motion.aside
        initial="closed"
        animate={isOpen ? 'open' : 'closed'}
        variants={sidebarVariants}
        transition={{ type: 'spring', stiffness: 300, damping: 30 }}
        className={`
          fixed lg:static inset-y-0 left-0 z-50
          ${isCollapsed ? 'w-20' : 'w-64'}
          bg-white dark:bg-neutral-900
          border-r border-neutral-200 dark:border-neutral-800
          transition-all duration-300
          lg:transform-none
        `}
      >
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="flex items-center justify-between h-16 px-4 border-b border-neutral-200 dark:border-neutral-800">
            {!isCollapsed && (
              <h2 className="text-lg font-semibold text-neutral-900 dark:text-neutral-100">
                Navigation
              </h2>
            )}
            <button
              onClick={onClose}
              className="lg:hidden p-2 rounded-md hover:bg-neutral-100 dark:hover:bg-neutral-800 transition-colors"
              aria-label="Close sidebar"
            >
              <X className="w-5 h-5 text-neutral-600 dark:text-neutral-400" />
            </button>
            {onToggleCollapse && (
              <button
                onClick={onToggleCollapse}
                className="hidden lg:block p-2 rounded-md hover:bg-neutral-100 dark:hover:bg-neutral-800 transition-colors"
                aria-label="Toggle sidebar"
              >
                <motion.div
                  animate={{ rotate: isCollapsed ? 180 : 0 }}
                  transition={{ duration: 0.3 }}
                >
                  <BarChart3 className="w-5 h-5 text-neutral-600 dark:text-neutral-400 rotate-90" />
                </motion.div>
              </button>
            )}
          </div>

          {/* Navigation */}
          <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
            {navItems.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center justify-between px-3 py-2 rounded-lg transition-all group ${
                    isActive
                      ? 'bg-primary-50 text-primary-700 dark:bg-primary-900/20 dark:text-primary-400'
                      : 'text-neutral-700 hover:bg-neutral-100 dark:text-neutral-300 dark:hover:bg-neutral-800'
                  }`
                }
              >
                <div className="flex items-center space-x-3">
                  <item.icon className="w-5 h-5 flex-shrink-0" />
                  <AnimatePresence>
                    {!isCollapsed && (
                      <motion.span
                        initial="collapsed"
                        animate="expanded"
                        exit="collapsed"
                        variants={contentVariants}
                        className="text-sm font-medium"
                      >
                        {item.label}
                      </motion.span>
                    )}
                  </AnimatePresence>
                </div>
                {!isCollapsed && item.badge && (
                  <span
                    className={`
                      px-2 py-0.5 text-xs font-medium rounded-full
                      ${getBadgeClasses(item.badgeType)}
                    `}
                  >
                    {item.badge}
                  </span>
                )}
              </NavLink>
            ))}
          </nav>

          {/* Footer */}
          <div className="p-4 border-t border-neutral-200 dark:border-neutral-800">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-neutral-200 dark:bg-neutral-700 rounded-full flex-shrink-0" />
              <AnimatePresence>
                {!isCollapsed && (
                  <motion.div
                    initial="collapsed"
                    animate="expanded"
                    exit="collapsed"
                    variants={contentVariants}
                    className="flex-1 min-w-0"
                  >
                    <p className="text-sm font-medium text-neutral-900 dark:text-neutral-100 truncate">
                      System Status
                    </p>
                    <p className="text-xs text-success-600 dark:text-success-400">
                      All systems operational
                    </p>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>
        </div>
      </motion.aside>
    </>
  );
};