import React, { createContext, useState, useCallback, useMemo, useEffect, useRef } from 'react';
import { toast } from 'react-toastify';
import api from '../utils/api';

interface User {
  id: number;
  email: string;
  username: string;
}

interface AuthContextType {
  isAuthenticated: boolean;
  user: User | null;
  login: (email: string, password: string) => Promise<{ success: boolean, error?: string }>;
  register: (username: string, email: string, password: string) => Promise<{ success: boolean, error?: string }>;
  logout: () => Promise<{ success: boolean, error?: string }>;
  checkAuthStatus: (bypassDebounce?: boolean) => Promise<{ success: boolean, error?: string, isLoggedOut?: boolean }>;
  revokeSession: (sessionId?: string) => Promise<{ success: boolean, error?: string, isCurrentSession?: boolean }>;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const lastCheckRef = useRef<number>(0);

  const checkAuthStatus = useCallback(async (bypassDebounce = false) => {
    console.trace('checkAuthStatus called', { bypassDebounce });
    const now = Date.now();
    if (!bypassDebounce && now - lastCheckRef.current < 2000) {
      console.log('Skipping auth status check: too frequent');
      return { success: false, error: 'Rate limited', isLoggedOut: false };
    }
    lastCheckRef.current = now;

    try {
      const response = await api.get('/auth/status');
      console.log('checkAuthStatus response:', response.data);
      const { id, username, email, is_active } = response.data;
      if (!is_active) {
        setUser(null);
        setIsAuthenticated(false);
        return { success: false, error: 'Account not activated', isLoggedOut: false };
      }
      setUser({ id, username, email });
      setIsAuthenticated(true);
      return { success: true, isLoggedOut: false };
    } catch (error: any) {
      console.error('Auth status check failed:', {
        message: error.message,
        status: error.response?.status,
        data: error.response?.data,
      });
      const isLoggedOut = error.response?.status === 401;
      if (isLoggedOut) {
        setUser(null);
        setIsAuthenticated(false);
        document.cookie = 'accessToken=; Max-Age=0; path=/;';
        document.cookie = 'refreshToken=; Max-Age=0; path=/;';
      }
      const errorMessage = isLoggedOut ? 'Session expired' : 'Failed to check auth status';
      return { success: false, error: errorMessage, isLoggedOut };
    }
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    try {
      setUser(null);
      setIsAuthenticated(false);
      document.cookie = 'accessToken=; Max-Age=0; path=/;';
      document.cookie = 'refreshToken=; Max-Age=0; path=/;';
      await api.post('/auth/login', { email, password });
      const result = await checkAuthStatus(true); // Bypass debounce
      console.log('Login checkAuthStatus result:', result);
      if (result.success) {
        toast.success('Logged in successfully!');
        return { success: true };
      } else {
        throw new Error(result.error || 'Login failed');
      }
    } catch (error: any) {
      console.error('Login Failed:', error.message || error.response?.data);
      const errorMessage = error.response?.data?.detail || error.message || 'Login failed';
      if (errorMessage.includes('not activated')) {
        toast.error('Please verify your email to activate your account.');
      } else {
        toast.error(errorMessage);
      }
      return { success: false, error: errorMessage };
    }
  }, [checkAuthStatus]);

  const register = useCallback(async (username: string, email: string, password: string) => {
    try {
      await api.post('/auth/register', { username, email, password });
      toast.success('Registration successful! Please check your email to verify your account.');
      return { success: true };
    } catch (error: any) {
      console.error('Registration Failed:', error.response?.data);
      const errorMessage = error.response?.data?.detail || 'Registration failed';
      toast.error(errorMessage);
      return { success: false, error: errorMessage };
    }
  }, []);

  const logout = useCallback(async () => {
    try {
      await api.post('/auth/logout');
      setUser(null);
      setIsAuthenticated(false);
      document.cookie = 'accessToken=; Max-Age=0; path=/;';
      document.cookie = 'refreshToken=; Max-Age=0; path=/;';
      toast.success('Logged out successfully!');
      return { success: true };
    } catch (error: any) {
      console.error('Logout error:', error.response?.data);
      const status = error.response?.status;
      const message = status === 401 ? 'Session already invalid or logged out' :
                      status === 500 ? 'Server error during logout' :
                      'Logout failed';
      toast.info(message);
      setUser(null);
      setIsAuthenticated(false);
      document.cookie = 'accessToken=; Max-Age=0; path=/;';
      document.cookie = 'refreshToken=; Max-Age=0; path=/;';
      return { success: true };
    }
  }, []);

  const revokeSession = useCallback(async (sessionId?: string) => {
    try {
      const response = await api.post('/auth/sessions/revoke', { session_id: sessionId });
      const { count } = response.data;
      toast.success(sessionId ? 'Session revoked' : `Revoked ${count} other session${count === 1 ? '' : 's'}`);
      if (sessionId) {
        const statusResult = await checkAuthStatus();
        const isCurrentSession = !statusResult.success;
        if (isCurrentSession) {
          setUser(null);
          setIsAuthenticated(false);
          document.cookie = 'accessToken=; Max-Age=0; path=/;';
          document.cookie = 'refreshToken=; Max-Age=0; path=/;';
        }
        return { success: true, isCurrentSession };
      }
      return { success: true };
    } catch (error: any) {
      console.error('Revoke Failed:', error.response?.data);
      const status = error.response?.status;
      const message = status === 401 ? 'Session expired or invalid. Please log in again.' :
                      status === 500 ? 'Server error. Please try again later.' :
                      'Failed to revoke session.';
      toast.info(message);
      if (status === 401 && sessionId) {
        const statusResult = await checkAuthStatus();
        if (!statusResult.success) {
          setUser(null);
          setIsAuthenticated(false);
          document.cookie = 'accessToken=; Max-Age=0; path=/;';
          document.cookie = 'refreshToken=; Max-Age=0; path=/;';
          return { success: false, error: message, isCurrentSession: true };
        }
      }
      return { success: false, error: message };
    }
  }, [checkAuthStatus]);

  useEffect(() => {
    if (isAuthenticated) {
      console.log('Skipping initial checkAuthStatus: already authenticated');
      return;
    }
    checkAuthStatus();
  }, [checkAuthStatus, isAuthenticated]);

  const value = useMemo(
    () => ({
      isAuthenticated,
      user,
      login,
      register,
      logout,
      checkAuthStatus,
      revokeSession,
    }),
    [isAuthenticated, user, login, register, logout, checkAuthStatus, revokeSession]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};