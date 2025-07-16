import React, { useEffect } from 'react';
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '@features/auth/hooks/useAuth';
import { Loading } from '@components/ui/Loading';

interface ProtectedRouteProps {
  requiredRole?: 'superuser' | 'admin' | 'developer' | 'viewer';
  children?: React.ReactNode;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ 
  requiredRole, 
  children 
}) => {
  const { isAuthenticated, user, loading, fetchUser, hasRole } = useAuth();
  const location = useLocation();

  useEffect(() => {
    // If we have a token but no user, fetch the user
    if (isAuthenticated && !user && !loading) {
      fetchUser().catch(() => {
        // Error handled in auth slice
      });
    }
  }, [isAuthenticated, user, loading, fetchUser]);

  // Show loading screen while checking auth status
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loading size="lg" />
      </div>
    );
  }

  // Redirect to login if not authenticated
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Check role requirements
  if (requiredRole && user && !hasRole(requiredRole)) {
    return <Navigate to="/unauthorized" replace />;
  }

  // Render children or outlet
  return children ? <>{children}</> : <Outlet />;
};