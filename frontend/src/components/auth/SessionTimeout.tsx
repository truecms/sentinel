import { useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import { useAuth } from '@features/auth/hooks/useAuth';

interface SessionTimeoutProps {
  timeoutMinutes?: number;
  warningMinutes?: number;
}

export const SessionTimeout: React.FC<SessionTimeoutProps> = ({
  timeoutMinutes = 30,
  warningMinutes = 5,
}) => {
  const navigate = useNavigate();
  const { signOut, isAuthenticated } = useAuth();
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const warningRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const lastActivityRef = useRef<number>(Date.now());

  const handleLogout = useCallback(async () => {
    await signOut();
    navigate('/login');
    toast.error('Your session has expired. Please login again.');
  }, [signOut, navigate]);

  const showWarning = useCallback(() => {
    toast.error(
      `Your session will expire in ${warningMinutes} minutes due to inactivity.`,
      {
        duration: 10000,
        id: 'session-warning',
      }
    );
  }, [warningMinutes]);

  const resetTimers = useCallback(() => {
    // Clear existing timers
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    if (warningRef.current) {
      clearTimeout(warningRef.current);
    }

    // Don't set timers if not authenticated
    if (!isAuthenticated) return;

    // Update last activity
    lastActivityRef.current = Date.now();

    // Set warning timer
    const warningTime = (timeoutMinutes - warningMinutes) * 60 * 1000;
    warningRef.current = setTimeout(showWarning, warningTime);

    // Set logout timer
    const logoutTime = timeoutMinutes * 60 * 1000;
    timeoutRef.current = setTimeout(handleLogout, logoutTime);
  }, [isAuthenticated, timeoutMinutes, warningMinutes, showWarning, handleLogout]);

  // Track user activity
  useEffect(() => {
    const events = ['mousedown', 'keydown', 'scroll', 'touchstart'];

    const handleActivity = () => {
      // Only reset if more than 1 minute has passed since last activity
      const now = Date.now();
      if (now - lastActivityRef.current > 60000) {
        resetTimers();
      }
    };

    // Add event listeners
    events.forEach((event) => {
      document.addEventListener(event, handleActivity);
    });

    // Initial timer setup
    resetTimers();

    // Cleanup
    return () => {
      events.forEach((event) => {
        document.removeEventListener(event, handleActivity);
      });
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
      if (warningRef.current) {
        clearTimeout(warningRef.current);
      }
    };
  }, [resetTimers]);

  // Reset timers when authentication state changes
  useEffect(() => {
    resetTimers();
  }, [isAuthenticated, resetTimers]);

  return null;
};