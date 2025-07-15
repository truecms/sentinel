import { api } from '@app/api';

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token?: string;
  token_type: string;
  user: {
    id: number;
    email: string;
    full_name: string;
    organization_id: number;
    role: string;
    is_active: boolean;
    created_at: string;
  };
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name: string;
  organization: {
    name: string;
  };
}

export interface ForgotPasswordRequest {
  email: string;
}

export interface ResetPasswordRequest {
  token: string;
  password: string;
}

export interface VerifyEmailRequest {
  token: string;
}

export const authApi = api.injectEndpoints({
  endpoints: (builder) => ({
    // Login endpoint
    login: builder.mutation<LoginResponse, LoginRequest>({
      query: (credentials) => {
        const formData = new FormData();
        formData.append('username', credentials.username);
        formData.append('password', credentials.password);
        
        return {
          url: '/auth/access-token',
          method: 'POST',
          body: formData,
        };
      },
    }),

    // Test token validity
    testToken: builder.query<{ message: string }, void>({
      query: () => '/auth/test-token',
    }),

    // Register new user
    register: builder.mutation<any, RegisterRequest>({
      query: (data) => ({
        url: '/users/',
        method: 'POST',
        body: data,
      }),
    }),

    // Request password reset
    forgotPassword: builder.mutation<{ message: string }, ForgotPasswordRequest>({
      query: (data) => ({
        url: '/auth/forgot-password',
        method: 'POST',
        body: data,
      }),
    }),

    // Reset password with token
    resetPassword: builder.mutation<{ message: string }, ResetPasswordRequest>({
      query: (data) => ({
        url: '/auth/reset-password',
        method: 'POST',
        body: data,
      }),
    }),

    // Verify email with token
    verifyEmail: builder.mutation<{ message: string }, VerifyEmailRequest>({
      query: (data) => ({
        url: '/auth/verify-email',
        method: 'POST',
        body: data,
      }),
    }),

    // Refresh access token
    refreshToken: builder.mutation<LoginResponse, { refresh_token: string }>({
      query: (data) => ({
        url: '/auth/refresh',
        method: 'POST',
        body: data,
      }),
    }),
  }),
});

export const {
  useLoginMutation,
  useTestTokenQuery,
  useRegisterMutation,
  useForgotPasswordMutation,
  useResetPasswordMutation,
  useVerifyEmailMutation,
  useRefreshTokenMutation,
} = authApi;