// L2/client/src/context/AuthContext.tsx
import React, { createContext, useState, useCallback, useMemo } from 'react';
import { toast } from 'react-toastify';
import api from '../utils/api';
import jwtDecode from 'jwt-decode';
import axios from 'axios';

interface User {
  id: number;
  email: string;
  username: string;
}

interface AuthContextType {
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  user: { username: string } | null;
  login: (email: string, password: string) => Promise<{ success: boolean, error?: string }>;
  register: (username: string, email: string, password: string) => Promise<{ success: boolean, error?: string }>;
  logout: () => Promise<{ success: boolean, error?: string }>;
  refresh: () => Promise<{ success: boolean, error?: string }>;
  revokeSession: (sessionId?: string) => Promise<{ success: boolean, error?: string, isCurrentSession?: boolean }>;
}

interface JwtPayload {
  sub: string;
  jti: string;
  iat?: number;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [refreshToken, setRefreshToken] = useState<string | null>(null);
  const [user, setUser] = useState<{ username: string } | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const login = useCallback(async (email: string, password: string) => {
    try {
      setAccessToken(null);
      setRefreshToken(null);
      setUser(null);
      setIsAuthenticated(false);

      const response = await api.post('/auth/login', { email, password });
      const { access_token, refresh_token, username } = response.data;
      const accessPayload: JwtPayload = jwtDecode(access_token);
      const refreshPayload: JwtPayload = jwtDecode(refresh_token);
      if (accessPayload.jti !== refreshPayload.jti) {
        console.error('JTI mismatch:', { accessJti: accessPayload.jti, refreshJti: refreshPayload.jti });
        throw new Error('Token JTI mismatch');
      }
      setAccessToken(access_token);
      setRefreshToken(refresh_token);
      setUser({ username });
      setIsAuthenticated(true);
      console.log('Login stored tokens:', {
        accessToken: access_token.substring(0, 10),
        accessJti: accessPayload.jti,
        refreshToken: refresh_token.substring(0, 10),
        refreshJti: refreshPayload.jti,
        username
      });
      toast.success('Logged in successfully!');
      return { success: true };
    } catch (error: any) {
      console.error('Login Failed:', error.response?.data || error.message);
      const errorMessage = error.response?.data?.detail || 'Login failed';
      if (errorMessage.includes('not activated')) {
        toast.error('Please verify your email to activate your account.');
      } else {
        toast.error(errorMessage);
      }
      return { success: false, error: errorMessage };
    }
  }, []);

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
    const accessPayload: JwtPayload = accessToken ? jwtDecode(accessToken) : { jti: 'none', sub: '' };
    console.log('Logout with accessToken:', accessToken?.substring(0, 10), 'jti:', accessPayload.jti);
    let retries = 1;
    while (retries >= 0) {
      try {
        if (accessToken) {
          await api.post('/auth/logout', {}, {
            headers: { Authorization: `Bearer ${accessToken}` },
          });
          console.log('Logout API call succeeded, jti:', accessPayload.jti);
        }
        break;
      } catch (error: any) {
        console.error('Logout error:', {
          status: error.response?.status,
          data: error.response?.data,
          retries,
        });
        const status = error.response?.status;
        if (status === 401) {
          toast.error('Session expired. Logged out.');
          break;
        } else if (status === 500) {
          toast.error('Server error during logout. Clearing session.');
        }
        retries--;
        if (retries < 0) {
          console.warn('Logout API failed, clearing state anyway');
          toast.error('Logout failed, session cleared.');
        }
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
    }
    setAccessToken(null);
    setRefreshToken(null);
    setUser(null);
    setIsAuthenticated(false);
    console.log('Logged out, cleared tokens');
    toast.success('Logged out successfully!');
    return { success: true };
  }, [accessToken]);

  const refresh = useCallback(async () => {
    if (!refreshToken || !isAuthenticated) {
      console.error('No refresh token or not authenticated');
      setAccessToken(null);
      setRefreshToken(null);
      setUser(null);
      setIsAuthenticated(false);
      return { success: false, error: 'No refresh token' };
    }

    try {
      const refreshPayload: JwtPayload = jwtDecode(refreshToken);
      console.log('Refreshing with token:', refreshToken.substring(0, 10), 'jti:', refreshPayload.jti);
      const response = await api.post('/auth/refresh', { refresh_token: refreshToken });
      const { access_token, refresh_token, username } = response.data;
      const accessPayload: JwtPayload = jwtDecode(access_token);
      const newRefreshPayload: JwtPayload = jwtDecode(refresh_token);
      if (accessPayload.jti !== newRefreshPayload.jti) {
        console.error('Refresh JTI mismatch:', { accessJti: accessPayload.jti, refreshJti: newRefreshPayload.jti });
        throw new Error('Refresh token JTI mismatch');
      }
      setAccessToken(access_token);
      setRefreshToken(refresh_token);
      setUser({ username });
      setIsAuthenticated(true);
      console.log('Refresh stored tokens:', {
        accessToken: access_token.substring(0, 10),
        accessJti: accessPayload.jti,
        refreshToken: refresh_token.substring(0, 10),
        refreshJti: newRefreshPayload.jti,
        username
      });
      return { success: true };
    } catch (error: any) {
      console.error('Refresh Failed:', {
        status: error.response?.status,
        data: error.response?.data,
      });
      const status = error.response?.status;
      const message = status === 401 ? 'Session expired. Please log in again.' :
                      status === 500 ? 'Server error. Please try again later.' :
                      'Failed to refresh session.';
      toast.error(message);
      setAccessToken(null);
      setRefreshToken(null);
      setUser(null);
      setIsAuthenticated(false);
      return { success: false, error: message };
    }
  }, [refreshToken, isAuthenticated]);

  const revokeSession = useCallback(async (sessionId?: string) => {
    try {
      const response = await api.post(
        '/auth/sessions/revoke',
        { session_id: sessionId },
        { headers: { Authorization: `Bearer ${accessToken}` } }
      );
      const { count } = response.data;
      toast.success(sessionId ? 'Session revoked' : `Revoked ${count} other session${count === 1 ? '' : 's'}`);

      const isCurrentSession = !!sessionId && sessionId === (accessToken ? jwtDecode<JwtPayload>(accessToken).jti : null);
      
      if (isCurrentSession) {
        setAccessToken(null);
        setRefreshToken(null);
        setUser(null);
        setIsAuthenticated(false);
      }
      return { success: true, isCurrentSession };
    } catch (error: any) {
      console.error('Revoke Failed:', error.response?.data);
      const status = error.response?.status;
      const message = status === 401 ? 'Session expired. Logging out.' :
                      status === 500 ? 'Server error. Please try again later.' :
                      'Failed to revoke session.';
      toast.error(message);
      if (status === 401) {
        setAccessToken(null);
        setRefreshToken(null);
        setUser(null);
        setIsAuthenticated(false);
        return { success: false, error: message, isCurrentSession: true };
      }
      return { success: false, error: message };
    }
  }, [accessToken]);

  const value = useMemo(
    () => ({
      accessToken,
      refreshToken,
      isAuthenticated,
      user,
      login,
      register,
      logout,
      refresh,
      revokeSession,
    }),
    [accessToken, refreshToken, isAuthenticated, user, login, register, logout, refresh, revokeSession]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};