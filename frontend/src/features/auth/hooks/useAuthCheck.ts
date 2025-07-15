import { useEffect } from 'react';
import { useAppDispatch, useAppSelector } from '@app/hooks';
import { getCurrentUser, selectIsAuthenticated } from '../authSlice';
import { tokenStorage } from '@services/tokenStorage';

export const useAuthCheck = () => {
  const dispatch = useAppDispatch();
  const isAuthenticated = useAppSelector(selectIsAuthenticated);

  useEffect(() => {
    // Check if we have a token on app startup
    const token = tokenStorage.getToken();
    
    if (token && !isAuthenticated) {
      // Try to get current user with the token
      dispatch(getCurrentUser()).catch(() => {
        // Token is invalid, it will be cleared by the auth slice
      });
    }
  }, [dispatch, isAuthenticated]);
};