import React from 'react';
import type { PropsWithChildren } from 'react';
import { useAuthCheck } from '@features/auth/hooks/useAuthCheck';

export const AuthProvider: React.FC<PropsWithChildren> = ({ children }) => {
  // Check authentication status on app startup
  useAuthCheck();
  
  return <>{children}</>;
};