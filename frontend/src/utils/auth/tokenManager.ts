import { store } from '@app/store';
import { setCredentials, clearAuth } from '@features/auth/authSlice';
import TokenStorageService from '@services/tokenStorage';

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
    // Also store in sessionStorage for interceptor access
    TokenStorageService.setToken(access);
  }

  getAccessToken(): string | null {
    // First try to get from sessionStorage (primary source)
    const sessionToken = TokenStorageService.getToken();
    if (sessionToken) {
      return sessionToken;
    }
    // Fallback to Redux state
    return store.getState().auth.token;
  }

  getRefreshToken(): string | null {
    return store.getState().auth.refreshToken;
  }

  clearTokens() {
    store.dispatch(clearAuth());
    TokenStorageService.removeToken();
  }

  async refreshToken(): Promise<string> {
    // Since there's no refresh token endpoint in the backend,
    // we can't refresh the token. Return null to force re-login.
    throw new Error('Token refresh not supported - please log in again');
  }

  private async _performRefresh(): Promise<string> {
    // This method is no longer used since refresh is not supported
    throw new Error('Token refresh not supported - please log in again');
  }

  isTokenExpired(token: string): boolean {
    try {
      // JWT structure: header.payload.signature
      const payload = JSON.parse(atob(token.split('.')[1]));
      const exp = payload.exp;
      
      if (!exp) {
        return false; // No expiration
      }
      
      // Check if token is actually expired (not just close to expiring)
      const expirationTime = exp * 1000; // Convert to milliseconds
      const currentTime = Date.now();
      
      return currentTime >= expirationTime; // Only expired if past expiration time
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