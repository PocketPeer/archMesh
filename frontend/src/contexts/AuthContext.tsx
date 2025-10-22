'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { apiClient } from '@/lib/api-client';

export interface User {
  id: string;
  email: string;
  name: string;
  is_verified: boolean;
}

export interface AuthContextType {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, name: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshAuthToken: () => Promise<void>;
  changePassword: (oldPassword: string, newPassword: string) => Promise<void>;
  requestPasswordReset: (email: string) => Promise<void>;
  resetPassword: (token: string, newPassword: string) => Promise<void>;
  verifyEmail: (token: string) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [refreshToken, setRefreshToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Consider authenticated if we have both user and access token
  const isAuthenticated = !!(user && accessToken);

  // Load auth state from localStorage on mount
  useEffect(() => {
    const loadAuthState = () => {
      try {
        const storedUser = localStorage.getItem('user');
        const storedAccessToken = localStorage.getItem('accessToken');
        const storedRefreshToken = localStorage.getItem('refreshToken');

        if (storedUser && storedAccessToken) {
          setUser(JSON.parse(storedUser));
          setAccessToken(storedAccessToken);
          setRefreshToken(storedRefreshToken);
        }
      } catch (error) {
        console.error('Failed to load auth state:', error);
        // Clear invalid auth state
        localStorage.removeItem('user');
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
      } finally {
        setIsLoading(false);
      }
    };

    const handleLogout = () => {
      setUser(null);
      setAccessToken(null);
      setRefreshToken(null);
      localStorage.removeItem('user');
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
    };

    loadAuthState();

    // Listen for logout events from API client
    window.addEventListener('auth:logout', handleLogout);

    return () => {
      window.removeEventListener('auth:logout', handleLogout);
    };
  }, []);

  // Auto-refresh token when it's about to expire
  useEffect(() => {
    if (!accessToken || !refreshToken) return;

    const refreshInterval = setInterval(async () => {
      try {
        await refreshAuthToken();
      } catch (error) {
        console.error('Auto token refresh failed:', error);
        // If auto-refresh fails, logout user
        await logout();
      }
    }, 50 * 60 * 1000); // Refresh every 50 minutes (tokens expire in 60 minutes)

    return () => clearInterval(refreshInterval);
  }, [accessToken, refreshToken]);

  const login = async (email: string, password: string) => {
    try {
      console.log('Login attempt for:', email);
      const response = await apiClient.login(email, password);
      console.log('Login response:', response);
      const raw: any = response as any;
      const data = raw.data || raw;

      if (data.success !== false && (data.data?.access_token || data.access_token || raw.access_token)) {
        const access = data.data?.access_token || data.access_token || raw.access_token;
        const refresh = data.data?.refresh_token || data.refresh_token || raw.refresh_token || null;
        const userCandidate = data.data?.user || data.user || raw.user;
        const normalizedUser: User | null = userCandidate
          ? {
              id: String(userCandidate.id),
              email: String(userCandidate.email),
              name: String(userCandidate.name || ''),
              is_verified: Boolean(userCandidate.is_verified),
            }
          : null;

        if (normalizedUser) setUser(normalizedUser);
        setAccessToken(access);
        setRefreshToken(refresh);

        localStorage.setItem('accessToken', access);
        if (refresh) localStorage.setItem('refreshToken', refresh);
        if (normalizedUser) localStorage.setItem('user', JSON.stringify(normalizedUser));
      } else {
        throw new Error(response.error || 'Login failed');
      }
    } catch (error) {
      throw error;
    }
  };

  const register = async (email: string, password: string, name: string) => {
    try {
      const response = await apiClient.register(email, password, name);
      
      if (response.success && (response as any)) {
        // Normalize backend payload: backend may return `data` instead of `user`
        const raw: any = response as any;
        const normalizedUser: User | null = raw.user
          ? raw.user
          : raw.data
            ? {
                id: String(raw.data.id),
                email: String(raw.data.email),
                name: String(raw.data.name || ''),
                is_verified: Boolean(raw.data.is_verified),
              }
            : null;

        if (!normalizedUser) {
          throw new Error(raw.error || 'Registration failed');
        }

        // Registration successful, now automatically login to get tokens
        try {
          console.log('Attempting auto-login after registration...');
          await login(email, password);
          console.log('Auto-login successful');
        } catch (loginError) {
          // If auto-login fails, still set user but they'll need to login manually
          console.warn('Auto-login after registration failed:', loginError);
          setUser(normalizedUser);
          localStorage.setItem('user', JSON.stringify(normalizedUser));
          throw new Error('Registration successful, but automatic login failed. Please login manually.');
        }
      } else {
        throw new Error(response.error || 'Registration failed');
      }
    } catch (error) {
      throw error;
    }
  };

  const logout = async () => {
    try {
      if (accessToken) {
        await apiClient.logout(accessToken);
      }
    } catch (error) {
      console.error('Logout API call failed:', error);
      // Continue with logout even if API call fails
    } finally {
      // Clear state
      setUser(null);
      setAccessToken(null);
      setRefreshToken(null);
      
      // Clear localStorage
      localStorage.removeItem('user');
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
    }
  };

  const refreshAuthToken = async () => {
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    try {
      const success = await apiClient.refreshToken();
      
      if (success) {
        // Get the updated tokens from localStorage (set by apiClient.refreshToken)
        const updatedAccessToken = localStorage.getItem('accessToken');
        const updatedRefreshToken = localStorage.getItem('refreshToken');
        
        if (updatedAccessToken) {
          setAccessToken(updatedAccessToken);
        }
        if (updatedRefreshToken) {
          setRefreshToken(updatedRefreshToken);
        }
      } else {
        throw new Error('Token refresh failed');
      }
    } catch (error) {
      // If refresh fails, logout user
      await logout();
      throw error;
    }
  };

  const changePassword = async (oldPassword: string, newPassword: string) => {
    if (!accessToken) {
      throw new Error('Not authenticated');
    }

    try {
      const response = await apiClient.changePassword(oldPassword, newPassword, accessToken);
      
      if (!response.success) {
        throw new Error(response.error || 'Password change failed');
      }
    } catch (error) {
      throw error;
    }
  };

  const requestPasswordReset = async (email: string) => {
    try {
      const response = await apiClient.requestPasswordReset(email);
      
      if (!response.success) {
        throw new Error(response.error || 'Password reset request failed');
      }
    } catch (error) {
      throw error;
    }
  };

  const resetPassword = async (token: string, newPassword: string) => {
    try {
      const response = await apiClient.resetPassword(token, newPassword);
      
      if (!response.success) {
        throw new Error(response.error || 'Password reset failed');
      }
    } catch (error) {
      throw error;
    }
  };

  const verifyEmail = async (token: string) => {
    try {
      const response = await apiClient.verifyEmail(token);
      
      if (!response.success) {
        throw new Error(response.error || 'Email verification failed');
      }
    } catch (error) {
      throw error;
    }
  };

  const value: AuthContextType = {
    user,
    accessToken,
    refreshToken,
    isLoading,
    isAuthenticated,
    login,
    register,
    logout,
    refreshAuthToken,
    changePassword,
    requestPasswordReset,
    resetPassword,
    verifyEmail,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

