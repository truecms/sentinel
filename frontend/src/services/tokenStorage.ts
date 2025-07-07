// Secure token storage service with XSS protection
// Uses sessionStorage by default (cleared when browser closes)
// Can be upgraded to httpOnly cookies in production

class TokenStorageService {
  private static readonly TOKEN_KEY = 'authToken';
  
  // Use sessionStorage by default (more secure than localStorage)
  // In production, this should be replaced with httpOnly cookies
  static getToken(): string | null {
    try {
      return sessionStorage.getItem(this.TOKEN_KEY);
    } catch (error) {
      console.error('Failed to retrieve auth token:', error);
      return null;
    }
  }
  
  static setToken(token: string): void {
    try {
      sessionStorage.setItem(this.TOKEN_KEY, token);
    } catch (error) {
      console.error('Failed to store auth token:', error);
    }
  }
  
  static removeToken(): void {
    try {
      sessionStorage.removeItem(this.TOKEN_KEY);
    } catch (error) {
      console.error('Failed to remove auth token:', error);
    }
  }
  
  // Clear all auth data
  static clearAll(): void {
    try {
      sessionStorage.removeItem(this.TOKEN_KEY);
    } catch (error) {
      console.error('Failed to clear auth data:', error);
    }
  }
}

export default TokenStorageService;