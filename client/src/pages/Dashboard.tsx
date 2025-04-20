// L2/client/src/pages/Dashboard.tsx
import React, { useContext, useEffect, useState, useCallback } from 'react';
import { AuthContext } from '../context/AuthContext';
import { toast } from 'react-toastify';
import api from '../utils/api';
import jwtDecode from 'jwt-decode';

interface Session {
  id: string;
  ip_address: string;
  user_agent: string;
  created_at: string;
}

const Dashboard: React.FC = () => {
  const authContext = useContext(AuthContext);
  const [sessions, setSessions] = useState<Session[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  if (!authContext) {
    throw new Error('AuthContext must be used within AuthProvider');
  }

  const { user, accessToken, revokeSession, logout } = authContext;

  const fetchSessions = useCallback(async () => {
    if (!accessToken) {
      toast.error('No access token available');
      return;
    }
    if (isLoading) return; // Prevent concurrent fetches
    setIsLoading(true);
    try {
      const response = await api.get('/auth/sessions', {
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      // Stable state update
      setSessions((prev) => {
        const newSessions = response.data.sessions;
        // Only update if sessions differ to prevent render loops
        if (JSON.stringify(prev) !== JSON.stringify(newSessions)) {
          return newSessions;
        }
        return prev;
      });
    } catch (error: any) {
      console.error('Failed to fetch sessions:', error.response?.data);
      toast.error(error.response?.data?.detail || 'Failed to load sessions');
    } finally {
      setIsLoading(false);
    }
  }, [accessToken]); // Removed isLoading dependency

  useEffect(() => {
    fetchSessions();
    // Optional: Poll every 30s for real-time updates (controlled)
    const interval = setInterval(fetchSessions, 30000);
    return () => clearInterval(interval); // Cleanup
  }, [fetchSessions]);

  const handleRevoke = async (sessionId: string) => {
    if (isLoading) return;
    try {
      await revokeSession(sessionId);
      // Update sessions locally to avoid re-fetch
      setSessions((prev) => prev.filter((s) => s.id !== sessionId));
    } catch (error) {
      // Error handled in revokeSession
    }
  };

  const handleRevokeAll = async () => {
    if (isLoading) return;
    try {
      await revokeSession();
      // Keep only current session
      const currentJti = accessToken ? jwtDecode<{ jti: string }>(accessToken).jti : '';
      setSessions((prev) => prev.filter((s) => s.id === currentJti));
    } catch (error) {
      // Error handled in revokeSession
    }
  };

  return (
    <div>
      <h1>Welcome, {user?.username}</h1>
      <button
        onClick={logout}
        disabled={isLoading}
        className="mb-4 bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600 disabled:bg-gray-400"
      >
        Log Out
      </button>
      <h2>Active Sessions</h2>
      {isLoading && sessions.length === 0 ? (
        <p>Loading sessions...</p>
      ) : sessions.length === 0 ? (
        <p>No active sessions</p>
      ) : (
        <ul>
          {sessions.map((session) => (
            <li key={session.id}>
              <p>IP: {session.ip_address}</p>
              <p>Device: {session.user_agent}</p>
              <p>Created: {new Date(session.created_at).toLocaleString()}</p>
              <button
                onClick={() => handleRevoke(session.id)}
                disabled={isLoading}
                className="bg-yellow-500 text-white px-2 py-1 rounded hover:bg-yellow-600 disabled:bg-gray-400"
              >
                Revoke
              </button>
            </li>
          ))}
        </ul>
      )}
      <button
        onClick={handleRevokeAll}
        disabled={isLoading}
        className="mt-4 bg-orange-500 text-white px-4 py-2 rounded hover:bg-orange-600 disabled:bg-gray-400"
      >
        Revoke All Other Sessions
      </button>
    </div>
  );
};

export default Dashboard;