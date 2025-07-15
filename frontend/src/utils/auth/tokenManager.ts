import { store } from '@app/store';
import { setCredentials, updateAccessToken, clearAuth } from '@features/auth/authSlice';

class TokenManager {
  private static TOKEN_KEY = 'auth_token';
  private static REFRESH_KEY = 'refresh_token';
  private refreshPromise: Promise<string> | null = null;

  setTokens(access: string, refresh?: string) {
    // Store in Redux state (memory only for security)
    store.dispatch(setCredentials({ 
      access_token: access, 
      refresh_token: refresh 
    }));
  }

  getAccessToken(): string | null {
    return store.getState().auth.token;
  }

  getRefreshToken(): string | null {
    return store.getState().auth.refreshToken;
  }

  clearTokens() {
    store.dispatch(clearAuth());
  }

  async refreshToken(): Promise<string> {
    // Prevent multiple simultaneous refresh attempts
    if (this.refreshPromise) {
      return this.refreshPromise;
    }

    this.refreshPromise = this._performRefresh();
    
    try {
      const token = await this.refreshPromise;
      return token;
    } finally {
      this.refreshPromise = null;
    }
  }

  private async _performRefresh(): Promise<string> {
    const refreshToken = this.getRefreshToken();
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    try {
      const response = await fetch('/api/v1/auth/refresh', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });

      if (!response.ok) {
        throw new Error('Token refresh failed');
      }

      const data = await response.json();
      const { access_token, refresh_token } = data;
      
      // Update tokens in store
      if (refresh_token) {
        this.setTokens(access_token, refresh_token);
      } else {
        store.dispatch(updateAccessToken(access_token));
      }
      
      return access_token;
    } catch (error) {
      // Clear auth on refresh failure
      this.clearTokens();
      throw error;
    }
  }

  isTokenExpired(token: string): boolean {
    try {
      // JWT structure: header.payload.signature
      const payload = JSON.parse(atob(token.split('.')[1]));
      const exp = payload.exp;
      
      if (!exp) {
        return false; // No expiration
      }
      
      // Check if token expires in less than 5 minutes
      const expirationTime = exp * 1000; // Convert to milliseconds
      const currentTime = Date.now();
      const timeUntilExpiry = expirationTime - currentTime;
      
      return timeUntilExpiry < 5 * 60 * 1000; // Less than 5 minutes
    } catch {
      return true; // If we can't parse the token, consider it expired
    }
  }

  async getValidToken(): Promise<string | null> {
    const token = this.getAccessToken();
    
    if (!token) {
      return null;
    }
    
    if (this.isTokenExpired(token)) {
      try {
        return await this.refreshToken();
      } catch {
        return null;
      }
    }
    
    return token;
  }
}

export const tokenManager = new TokenManager();