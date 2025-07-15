import React from 'react';
import type { PropsWithChildren } from 'react';
import { useAuthCheck } from '@features/auth/hooks/useAuthCheck';
import { SessionTimeout } from './SessionTimeout';

export const AuthProvider: React.FC<PropsWithChildren> = ({ children }) => {
  // Check authentication status on app startup
  useAuthCheck();
  
  return (
    <>
      <SessionTimeout timeoutMinutes={30} warningMinutes={5} />
      {children}
    </>
  );
};