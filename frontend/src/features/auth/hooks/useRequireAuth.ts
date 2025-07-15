import { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from './useAuth';

export const useRequireAuth = (requiredRole?: string) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { isAuthenticated, user, loading, hasRole } = useAuth();

  useEffect(() => {
    if (!loading) {
      if (!isAuthenticated) {
        // Save the current location to redirect back after login
        navigate('/login', { state: { from: location }, replace: true });
      } else if (requiredRole && user && !hasRole(requiredRole)) {
        navigate('/unauthorized', { replace: true });
      }
    }
  }, [isAuthenticated, loading, navigate, location, requiredRole, user, hasRole]);

  return { isAuthenticated, user, loading };
};