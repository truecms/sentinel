import { useAppSelector, useAppDispatch } from '@app/hooks';
import { selectAuth, selectUser, selectIsAuthenticated, login, logout, getCurrentUser, register } from '../authSlice';
import { useCallback } from 'react';

export const useAuth = () => {
  const dispatch = useAppDispatch();
  const auth = useAppSelector(selectAuth);
  const user = useAppSelector(selectUser);
  const isAuthenticated = useAppSelector(selectIsAuthenticated);

  const signIn = useCallback(
    async (email: string, password: string, remember?: boolean) => {
      const result = await dispatch(login({ email, password, remember }));
      if (login.fulfilled.match(result)) {
        return result.payload;
      }
      throw new Error(result.error?.message || 'Login failed');
    },
    [dispatch]
  );

  const signOut = useCallback(async () => {
    await dispatch(logout());
  }, [dispatch]);

  const fetchUser = useCallback(async () => {
    const result = await dispatch(getCurrentUser());
    if (getCurrentUser.fulfilled.match(result)) {
      return result.payload;
    }
    throw new Error(result.error?.message || 'Failed to fetch user');
  }, [dispatch]);

  const signUp = useCallback(
    async (data: { email: string; password: string; full_name: string; organization_name: string }) => {
      const result = await dispatch(register(data));
      if (register.fulfilled.match(result)) {
        return result.payload;
      }
      throw new Error(result.error?.message || 'Registration failed');
    },
    [dispatch]
  );

  const hasRole = useCallback(
    (requiredRole: string) => {
      if (!user) return false;
      
      const roleHierarchy = {
        superuser: 4,
        admin: 3,
        developer: 2,
        viewer: 1,
      };

      const userLevel = roleHierarchy[user.role] || 0;
      const requiredLevel = roleHierarchy[requiredRole as keyof typeof roleHierarchy] || 0;

      return userLevel >= requiredLevel;
    },
    [user]
  );

  return {
    ...auth,
    user,
    isAuthenticated,
    signIn,
    signUp,
    signOut,
    fetchUser,
    hasRole,
  };
};