import React, { useState, useEffect } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { TopBar, Sidebar, MobileNav, Breadcrumbs } from '../../components/navigation';
import type { BreadcrumbItem } from '../../components/navigation/Breadcrumbs/Breadcrumbs';
import { useAuth } from '../../features/auth/hooks/useAuth';

interface DashboardLayoutProps {
  breadcrumbs?: BreadcrumbItem[];
}

export const DashboardLayout: React.FC<DashboardLayoutProps> = ({ breadcrumbs = [] }) => {
  const location = useLocation();
  const { user } = useAuth();
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(false);

  // Initialize theme from localStorage or system preference
  useEffect(() => {
    const savedTheme = localStorage.getItem('theme');
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    if (savedTheme === 'dark' || (!savedTheme && systemPrefersDark)) {
      setIsDarkMode(true);
      document.documentElement.classList.add('dark');
    }
  }, []);

  // Handle theme toggle
  const handleThemeToggle = () => {
    const newTheme = !isDarkMode;
    setIsDarkMode(newTheme);
    
    if (newTheme) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    }
  };

  // Handle sidebar collapse from localStorage
  useEffect(() => {
    const savedCollapsed = localStorage.getItem('sidebarCollapsed');
    if (savedCollapsed === 'true') {
      setIsSidebarCollapsed(true);
    }
  }, []);

  const handleSidebarCollapse = () => {
    const newCollapsed = !isSidebarCollapsed;
    setIsSidebarCollapsed(newCollapsed);
    localStorage.setItem('sidebarCollapsed', String(newCollapsed));
  };

  return (
    <div className="min-h-screen bg-neutral-50 dark:bg-neutral-900">
      {/* Top Bar */}
      <TopBar
        onMenuToggle={() => setIsSidebarOpen(!isSidebarOpen)}
        isDarkMode={isDarkMode}
        onThemeToggle={handleThemeToggle}
        notificationCount={3}
        userName={user?.full_name || user?.email || 'User'}
        userEmail={user?.email || ''}
      />

      <div className="flex h-[calc(100vh-4rem)]">
        {/* Sidebar - Desktop */}
        <div className="hidden lg:block">
          <Sidebar
            isOpen={true}
            onClose={() => {}}
            isCollapsed={isSidebarCollapsed}
            onToggleCollapse={handleSidebarCollapse}
          />
        </div>

        {/* Sidebar - Mobile */}
        <Sidebar
          isOpen={isSidebarOpen}
          onClose={() => setIsSidebarOpen(false)}
        />

        {/* Main Content */}
        <main className="flex-1 overflow-y-auto">
          <div className="p-4 sm:p-6 lg:p-8">
            {/* Breadcrumbs */}
            {breadcrumbs.length > 0 && (
              <Breadcrumbs items={breadcrumbs} className="mb-6" />
            )}

            {/* Page Content with Animation */}
            <AnimatePresence mode="wait">
              <motion.div
                key={location.pathname}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.2 }}
              >
                <Outlet />
              </motion.div>
            </AnimatePresence>
          </div>
        </main>
      </div>

      {/* Mobile Navigation */}
      <MobileNav />

      {/* Add padding bottom for mobile nav */}
      <div className="h-16 lg:hidden" />
    </div>
  );
};