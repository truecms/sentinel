import type { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';
import { tokenManager } from '@utils/auth/tokenManager';

interface RetryableRequest extends InternalAxiosRequestConfig {
  _retry?: boolean;
}

export const setupInterceptors = (apiClient: AxiosInstance) => {
  // Request interceptor - add auth token
  apiClient.interceptors.request.use(
    async (config) => {
      // Don't add token to login endpoint
      if (config.url?.includes('/auth/access-token')) {
        return config;
      }

      const token = await tokenManager.getValidToken();
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      
      return config;
    },
    (error) => {
      return Promise.reject(error);
    }
  );

  // Response interceptor - handle 401 and token refresh
  apiClient.interceptors.response.use(
    (response) => response,
    async (error: AxiosError) => {
      const originalRequest = error.config as RetryableRequest;
      
      if (!originalRequest) {
        return Promise.reject(error);
      }

      // Handle 401 Unauthorized
      if (error.response?.status === 401 && !originalRequest._retry) {
        // Don't retry for login requests
        if (originalRequest.url?.includes('/auth/access-token')) {
          return Promise.reject(error);
        }

        originalRequest._retry = true;

        try {
          const newToken = await tokenManager.refreshToken();
          
          // Retry original request with new token
          originalRequest.headers.Authorization = `Bearer ${newToken}`;
          return apiClient(originalRequest);
        } catch (refreshError) {
          // Refresh failed, clear tokens and redirect to login
          tokenManager.clearTokens();
          
          // Only redirect if we're in a browser environment
          if (typeof window !== 'undefined') {
            window.location.href = '/login';
          }
          
          return Promise.reject(refreshError);
        }
      }

      // Handle other errors
      if (error.response?.status === 403) {
        // Forbidden - user doesn't have permission
        console.error('Access forbidden:', error.response.data);
      } else if (error.response?.status === 422) {
        // Validation error
        console.error('Validation error:', error.response.data);
      }

      return Promise.reject(error);
    }
  );
};