import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { HelmetProvider } from 'react-helmet-async'
import { ThemeProvider } from './contexts/ThemeContext'
import { DashboardLayout } from './layouts/DashboardLayout'
import PublicLayout from './components/layout/PublicLayout'
import { Dashboard, Sites, Modules, Reports, Settings } from './pages'
import LandingPage from './features/public/pages/LandingPage'
import FeaturesPage from './features/public/pages/FeaturesPage'
import PricingPage from './features/public/pages/PricingPage'
import './App.css'

function App() {
  return (
    <HelmetProvider>
      <ThemeProvider>
        <BrowserRouter>
          <Routes>
            {/* Public Routes */}
            <Route path="/" element={<PublicLayout />}>
              <Route index element={<LandingPage />} />
              <Route path="features" element={<FeaturesPage />} />
              <Route path="pricing" element={<PricingPage />} />
            </Route>

            {/* Protected Routes */}
            <Route path="/app" element={<DashboardLayout />}>
              <Route index element={<Navigate to="/app/dashboard" replace />} />
              <Route path="dashboard" element={<Dashboard />} />
              <Route path="sites" element={<Sites />} />
              <Route path="modules" element={<Modules />} />
              <Route path="reports" element={<Reports />} />
              <Route path="settings" element={<Settings />} />
            </Route>

            {/* Redirect old dashboard route to new app route */}
            <Route path="/dashboard" element={<Navigate to="/app/dashboard" replace />} />
          </Routes>
        </BrowserRouter>
      </ThemeProvider>
    </HelmetProvider>
  )
}

export default App
