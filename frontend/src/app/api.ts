import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import type { RootState } from './types';

// Define a service using a base URL and expected endpoints
export const api = createApi({
  reducerPath: 'api',
  baseQuery: fetchBaseQuery({
    baseUrl: '/api/v1',
    prepareHeaders: (headers, { getState }) => {
      // Get token from auth state
      const state = getState() as RootState;
      const token = state.auth?.token;
      
      if (token) {
        headers.set('authorization', `Bearer ${token}`);
      }
      
      return headers;
    },
  }),
  tagTypes: ['User', 'Organization', 'Site', 'Module', 'ModuleVersion'],
  endpoints: () => ({
    // Endpoints will be injected by feature slices
  }),
});

// Export hooks for usage in functional components
// Individual hooks will be exported from feature slices