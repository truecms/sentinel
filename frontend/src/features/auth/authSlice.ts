import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { RootState } from '@app/store';
import { tokenStorage } from '@services/tokenStorage';
import { apiClient } from '@utils/api';
import { toast } from 'react-hot-toast';

export interface User {
  id: number;
  email: string;
  full_name: string;
  organization_id: number;
  role: 'superuser' | 'admin' | 'developer' | 'viewer';
  is_active: boolean;
  created_at: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  loading: boolean;
  error: string | null;
}

export interface LoginCredentials {
  email: string;
  password: string;
  remember?: boolean;
}

interface LoginResponse {
  access_token: string;
  refresh_token?: string;
  token_type: string;
  user: User;
}

export interface RegisterData {
  email: string;
  password: string;
  full_name: string;
  organization_name: string;
  accept_terms: boolean;
}

const initialState: AuthState = {
  user: null,
  token: tokenStorage.getToken(),
  refreshToken: null,
  isAuthenticated: false,
  loading: false,
  error: null,
};

// Async thunks
export const login = createAsyncThunk(
  'auth/login',
  async (credentials: LoginCredentials) => {
    const formData = new FormData();
    formData.append('username', credentials.email);
    formData.append('password', credentials.password);

    const response = await apiClient.post<LoginResponse>('/auth/access-token', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  }
);

export const getCurrentUser = createAsyncThunk(
  'auth/getCurrentUser',
  async () => {
    const response = await apiClient.get<User>('/auth/me');
    return response.data;
  }
);

export const logout = createAsyncThunk(
  'auth/logout',
  async () => {
    // Clear tokens
    tokenStorage.removeToken();
    // The backend doesn't have a logout endpoint, so we just clear local state
    return null;
  }
);

export const refreshToken = createAsyncThunk(
  'auth/refreshToken',
  async (_, { getState }) => {
    const state = getState() as RootState;
    const currentRefreshToken = state.auth.refreshToken;
    
    if (!currentRefreshToken) {
      throw new Error('No refresh token available');
    }

    const response = await apiClient.post<LoginResponse>('/auth/refresh', {
      refresh_token: currentRefreshToken,
    });

    return response.data;
  }
);

export const register = createAsyncThunk(
  'auth/register',
  async (data: RegisterData) => {
    const payload = {
      email: data.email,
      password: data.password,
      full_name: data.full_name,
      organization: {
        name: data.organization_name,
      },
    };

    const response = await apiClient.post<User>('/users/', payload);
    return response.data;
  }
);

export const changePassword = createAsyncThunk(
  'auth/changePassword',
  async ({ currentPassword, newPassword }: { currentPassword: string; newPassword: string }) => {
    const response = await apiClient.post('/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
    });
    return response.data;
  }
);

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    setCredentials: (state, action: PayloadAction<{ access_token: string; refresh_token?: string }>) => {
      state.token = action.payload.access_token;
      state.refreshToken = action.payload.refresh_token || null;
      state.isAuthenticated = true;
      tokenStorage.setToken(action.payload.access_token);
    },
    updateAccessToken: (state, action: PayloadAction<string>) => {
      state.token = action.payload;
      tokenStorage.setToken(action.payload);
    },
    clearAuth: (state) => {
      state.user = null;
      state.token = null;
      state.refreshToken = null;
      state.isAuthenticated = false;
      state.error = null;
      tokenStorage.removeToken();
    },
  },
  extraReducers: (builder) => {
    // Login
    builder
      .addCase(login.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(login.fulfilled, (state, action) => {
        state.loading = false;
        state.isAuthenticated = true;
        state.token = action.payload.access_token;
        state.refreshToken = action.payload.refresh_token || null;
        state.user = action.payload.user;
        state.error = null;
        tokenStorage.setToken(action.payload.access_token);
      })
      .addCase(login.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Login failed';
        state.isAuthenticated = false;
      });

    // Get current user
    builder
      .addCase(getCurrentUser.pending, (state) => {
        state.loading = true;
      })
      .addCase(getCurrentUser.fulfilled, (state, action) => {
        state.loading = false;
        state.user = action.payload;
        state.isAuthenticated = true;
        state.error = null;
      })
      .addCase(getCurrentUser.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to get user';
        // If we can't get the current user, the token is likely invalid
        state.isAuthenticated = false;
        state.token = null;
        tokenStorage.removeToken();
      });

    // Logout
    builder
      .addCase(logout.fulfilled, (state) => {
        state.user = null;
        state.token = null;
        state.refreshToken = null;
        state.isAuthenticated = false;
        state.error = null;
        state.loading = false;
      });

    // Refresh token
    builder
      .addCase(refreshToken.fulfilled, (state, action) => {
        state.token = action.payload.access_token;
        state.refreshToken = action.payload.refresh_token || state.refreshToken;
        tokenStorage.setToken(action.payload.access_token);
      })
      .addCase(refreshToken.rejected, (state) => {
        // If refresh fails, clear auth state
        state.user = null;
        state.token = null;
        state.refreshToken = null;
        state.isAuthenticated = false;
        tokenStorage.removeToken();
      });

    // Register
    builder
      .addCase(register.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(register.fulfilled, (state) => {
        state.loading = false;
        state.error = null;
        // Registration successful, but user needs to login
        toast.success('Registration successful! Please check your email to verify your account.');
      })
      .addCase(register.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Registration failed';
      });

    // Change password
    builder
      .addCase(changePassword.fulfilled, () => {
        toast.success('Password changed successfully');
      })
      .addCase(changePassword.rejected, (_, action) => {
        toast.error(action.error.message || 'Failed to change password');
      });
  },
});

export const { setCredentials, updateAccessToken, clearAuth } = authSlice.actions;

// Selectors
export const selectAuth = (state: RootState) => state.auth;
export const selectUser = (state: RootState) => state.auth.user;
export const selectIsAuthenticated = (state: RootState) => state.auth.isAuthenticated;
export const selectAuthLoading = (state: RootState) => state.auth.loading;
export const selectAuthError = (state: RootState) => state.auth.error;

export default authSlice.reducer;