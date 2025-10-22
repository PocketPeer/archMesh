import React from 'react';
import { render, screen, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { AuthProvider, useAuth } from '@/src/contexts/AuthContext';
import { apiClient } from '@/lib/api-client';

// Mock the API client
jest.mock('@/lib/api-client', () => ({
  apiClient: {
    login: jest.fn(),
    register: jest.fn(),
    logout: jest.fn(),
    refreshToken: jest.fn(),
    changePassword: jest.fn(),
    requestPasswordReset: jest.fn(),
    resetPassword: jest.fn(),
    verifyEmail: jest.fn(),
  },
}));

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

// Test component that uses the auth context
const TestComponent = () => {
  const { user, isAuthenticated, login, logout } = useAuth();
  const [error, setError] = React.useState<string | null>(null);

  const handleLogin = async () => {
    try {
      await login('test@example.com', 'password');
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
    }
  };

  return (
    <div>
      <div data-testid="user-info">
        {user ? `${user.name} (${user.email})` : 'No user'}
      </div>
      <div data-testid="auth-status">
        {isAuthenticated ? 'Authenticated' : 'Not authenticated'}
      </div>
      {error && <div data-testid="error">{error}</div>}
      <button onClick={handleLogin}>
        Login
      </button>
      <button onClick={logout}>Logout</button>
    </div>
  );
};

describe('AuthContext', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorageMock.getItem.mockReturnValue(null);
  });

  it('should provide initial unauthenticated state', () => {
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    expect(screen.getByTestId('user-info')).toHaveTextContent('No user');
    expect(screen.getByTestId('auth-status')).toHaveTextContent('Not authenticated');
  });

  it('should handle successful login', async () => {
    const user = userEvent.setup();
    const mockUser = {
      id: '1',
      email: 'test@example.com',
      name: 'Test User',
      is_verified: true,
    };

    (apiClient.login as jest.Mock).mockResolvedValue({
      success: true,
      access_token: 'access-token',
      refresh_token: 'refresh-token',
      user: mockUser,
    });

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    await user.click(screen.getByText('Login'));

    await waitFor(() => {
      expect(screen.getByTestId('user-info')).toHaveTextContent('Test User (test@example.com)');
      expect(screen.getByTestId('auth-status')).toHaveTextContent('Authenticated');
    });

    expect(apiClient.login).toHaveBeenCalledWith('test@example.com', 'password');
    expect(localStorageMock.setItem).toHaveBeenCalledWith('user', JSON.stringify(mockUser));
    expect(localStorageMock.setItem).toHaveBeenCalledWith('accessToken', 'access-token');
    expect(localStorageMock.setItem).toHaveBeenCalledWith('refreshToken', 'refresh-token');
  });

  it('should handle login failure', async () => {
    const user = userEvent.setup();

    // Mock the login to reject with an error
    (apiClient.login as jest.Mock).mockImplementation(() => 
      Promise.reject(new Error('Invalid credentials'))
    );

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    await user.click(screen.getByText('Login'));

    await waitFor(() => {
      expect(screen.getByTestId('user-info')).toHaveTextContent('No user');
      expect(screen.getByTestId('auth-status')).toHaveTextContent('Not authenticated');
      expect(screen.getByTestId('error')).toHaveTextContent('Invalid credentials');
    });

    expect(apiClient.login).toHaveBeenCalledWith('test@example.com', 'password');
  });

  it('should handle logout', async () => {
    const user = userEvent.setup();
    const mockUser = {
      id: '1',
      email: 'test@example.com',
      name: 'Test User',
      is_verified: true,
    };

    // Set up authenticated state
    localStorageMock.getItem.mockImplementation((key) => {
      if (key === 'user') return JSON.stringify(mockUser);
      if (key === 'accessToken') return 'access-token';
      if (key === 'refreshToken') return 'refresh-token';
      return null;
    });

    (apiClient.logout as jest.Mock).mockResolvedValue({ success: true });

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    // Wait for initial state to load
    await waitFor(() => {
      expect(screen.getByTestId('auth-status')).toHaveTextContent('Authenticated');
    });

    await user.click(screen.getByText('Logout'));

    await waitFor(() => {
      expect(screen.getByTestId('user-info')).toHaveTextContent('No user');
      expect(screen.getByTestId('auth-status')).toHaveTextContent('Not authenticated');
    });

    expect(apiClient.logout).toHaveBeenCalledWith('access-token');
    expect(localStorageMock.removeItem).toHaveBeenCalledWith('user');
    expect(localStorageMock.removeItem).toHaveBeenCalledWith('accessToken');
    expect(localStorageMock.removeItem).toHaveBeenCalledWith('refreshToken');
  });

  it('should load auth state from localStorage on mount', async () => {
    const mockUser = {
      id: '1',
      email: 'test@example.com',
      name: 'Test User',
      is_verified: true,
    };

    localStorageMock.getItem.mockImplementation((key) => {
      if (key === 'user') return JSON.stringify(mockUser);
      if (key === 'accessToken') return 'access-token';
      if (key === 'refreshToken') return 'refresh-token';
      return null;
    });

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('user-info')).toHaveTextContent('Test User (test@example.com)');
      expect(screen.getByTestId('auth-status')).toHaveTextContent('Authenticated');
    });
  });

  it('should throw error when useAuth is used outside AuthProvider', () => {
    // Suppress console.error for this test
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

    expect(() => {
      render(<TestComponent />);
    }).toThrow('useAuth must be used within an AuthProvider');

    consoleSpy.mockRestore();
  });
});
