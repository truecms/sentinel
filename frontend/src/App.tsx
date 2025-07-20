import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { HelmetProvider } from 'react-helmet-async'
import { Toaster } from 'react-hot-toast'
import { ThemeProvider } from './contexts/ThemeContext'
import { toastConfig } from './components/common/Toast'
import { DashboardLayout } from './layouts/DashboardLayout'
import PublicLayout from './components/layout/PublicLayout'
import { Dashboard, Sites, Modules, Reports, Settings, Organizations } from './pages'
import { OrganizationDetails } from './pages/Organizations/OrganizationDetails'
import LandingPage from './features/public/pages/LandingPage'
import FeaturesPage from './features/public/pages/FeaturesPage'
import PricingPage from './features/public/pages/PricingPage'
import { LoginPage } from './features/auth/pages/LoginPage'
import { RegisterPage } from './features/auth/pages/RegisterPage'
import { ForgotPasswordPage } from './features/auth/pages/ForgotPasswordPage'
import { ResetPasswordPage } from './features/auth/pages/ResetPasswordPage'
import { ProtectedRoute } from './components/auth/ProtectedRoute'
import { SessionTimeout } from './components/auth/SessionTimeout'
import './App.css'

function App() {
  return (
    <HelmetProvider>
      <ThemeProvider>
        <BrowserRouter>
          <Toaster {...toastConfig} />
          <SessionTimeout timeoutMinutes={30} warningMinutes={5} />
          <Routes>
            {/* Public Routes */}
            <Route path="/" element={<PublicLayout />}>
              <Route index element={<LandingPage />} />
              <Route path="features" element={<FeaturesPage />} />
              <Route path="pricing" element={<PricingPage />} />
            </Route>

            {/* Auth Routes */}
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/forgot-password" element={<ForgotPasswordPage />} />
            <Route path="/reset-password" element={<ResetPasswordPage />} />

            {/* Protected Routes */}
            <Route path="/app" element={<ProtectedRoute />}>
              <Route element={<DashboardLayout />}>
                <Route index element={<Navigate to="/app/dashboard" replace />} />
                <Route path="dashboard" element={<Dashboard />} />
                <Route path="organizations" element={<Organizations />} />
                <Route path="organizations/:id" element={<OrganizationDetails />} />
                <Route path="sites" element={<Sites />} />
                <Route path="modules" element={<Modules />} />
                <Route path="reports" element={<Reports />} />
                <Route path="settings" element={<Settings />} />
              </Route>
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