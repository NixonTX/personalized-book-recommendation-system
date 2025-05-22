// L2/client/src/pages/Dashboard.tsx
import React, { useContext, useEffect, useState, useCallback } from 'react';
import { AuthContext } from '../context/AuthContext';
import { toast } from 'react-toastify';
import api from '../utils/api';
import jwtDecode from 'jwt-decode';
import { useNavigate } from 'react-router-dom';

interface Session {
  id: string;
  ip_address: string;
  user_agent: string;
  created_at: string;
}

const Dashboard: React.FC = () => {
  const authContext = useContext(AuthContext);
  const navigate = useNavigate();
  const [sessions, setSessions] = useState<Session[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  if (!authContext) {
    throw new Error('AuthContext must be used within AuthProvider');
  }

  const { user, accessToken, logout } = authContext;

  const fetchSessions = useCallback(async () => {
    if (!accessToken) {
      toast.error('No access token available');
      return;
    }
    if (isLoading) return;
    setIsLoading(true);
    try {
      const response = await api.get('/auth/sessions', {
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      setSessions((prev) => {
        const newSessions = response.data.sessions;
        if (JSON.stringify(prev) !== JSON.stringify(newSessions)) {
          return newSessions;
        }
        return prev;
      });
    } catch (error: any) {
      console.error('Failed to fetch sessions:', error.response?.data);
      const status = error.response?.status;
      const message = status === 401 ? 'Session expired. Logging out.' :
                      status === 500 ? 'Server error. Please try again later.' :
                      'Failed to load sessions.';
      toast.error(message);
      if (status === 401) {
        logout();
        navigate('/auth/login');
      }
    } finally {
      setIsLoading(false);
    }
  }, [accessToken, logout, navigate]);

  useEffect(() => {
    fetchSessions();
    const interval = setInterval(fetchSessions, 30000);
    return () => clearInterval(interval);
  }, [fetchSessions]);

  const handleNavigateToSessions = () => {
    navigate('/sessions');
  };

  const handleLogout = async () => {
    try {
      const result = await logout();
      if (result.success) {
        navigate('/auth/login');
      }
    } catch (error) {
      // handled in AuthContext via toast
    }
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h1 style={{ fontSize: '24px', color: '#333' }}>Welcome, {user?.username}</h1>
        <div>
          <button
            onClick={handleNavigateToSessions}
            disabled={isLoading}
            style={{
              marginRight: '10px',
              padding: '8px 16px',
              backgroundColor: '#007bff',
              color: '#fff',
              border: 'none',
              borderRadius: '4px',
              cursor: isLoading ? 'not-allowed' : 'pointer',
              opacity: isLoading ? 0.6 : 1,
              fontSize: '14px',
            }}
            onMouseOver={(e) => (e.currentTarget.style.backgroundColor = '#0056b3')}
            onMouseOut={(e) => (e.currentTarget.style.backgroundColor = '#007bff')}
          >
            Manage Sessions
          </button>
          <button
            onClick={handleLogout}
            disabled={isLoading}
            style={{
              padding: '8px 16px',
              backgroundColor: '#dc3545',
              color: '#fff',
              border: 'none',
              borderRadius: '4px',
              cursor: isLoading ? 'not-allowed' : 'pointer',
              opacity: isLoading ? 0.6 : 1,
              fontSize: '14px',
            }}
            onMouseOver={(e) => (e.currentTarget.style.backgroundColor = '#a71d2a')}
            onMouseOut={(e) => (e.currentTarget.style.backgroundColor = '#dc3545')}
          >
            Log Out
          </button>
        </div>
      </div>
      {/* Placeholder for book search functionality */}
      <div>
        <h2 style={{ fontSize: '20px', color: '#333', marginBottom: '10px' }}>Search Books</h2>
        <p style={{ color: '#666' }}>Book search functionality to be implemented.</p>
      </div>
    </div>
  );
};

export default Dashboard;