// Auth feature exports
// Slice and actions
export {
  default as authReducer,
  login,
  logout,
  getCurrentUser,
  register,
  changePassword,
  setCredentials,
  updateAccessToken,
  clearAuth,
  selectAuth,
  selectUser,
  selectIsAuthenticated,
  selectAuthLoading,
  selectAuthError,
} from './authSlice';

// API endpoints
export {
  authApi,
  useLoginMutation,
  useTestTokenQuery,
  useRegisterMutation,
  useForgotPasswordMutation,
  useResetPasswordMutation,
  useVerifyEmailMutation,
  useRefreshTokenMutation,
} from './authApi';

// Hooks
export { useAuth } from './hooks/useAuth';

// Types
export type { User, AuthState, LoginCredentials, RegisterData } from './authSlice';
export type {
  LoginRequest,
  LoginResponse,
  RegisterRequest,
  ForgotPasswordRequest,
  ResetPasswordRequest,
  VerifyEmailRequest,
} from './authApi';