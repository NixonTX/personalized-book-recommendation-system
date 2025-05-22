// L2/client/src/pages/Sessions.tsx
import React, { useContext, useEffect, useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { AuthContext } from "/home/nixontx/Desktop/ML/L2/client/src/context/AuthContext.tsx";
import { toast } from "react-toastify";
import api from "/home/nixontx/Desktop/ML/L2/client/src/utils/api.ts";
import jwtDecode from "jwt-decode";

interface Session {
  id: string;
  ip_address: string;
  user_agent: string;
  created_at: string;
}

const Sessions: React.FC = () => {
  const authContext = useContext(AuthContext);
  const navigate = useNavigate();
  const [sessions, setSessions] = useState<Session[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  if (!authContext) {
    throw new Error("AuthContext must be used within AuthProvider");
  }

  const { accessToken, revokeSession } = authContext;

  const fetchSessions = useCallback(async () => {
    if (!accessToken) {
      toast.error("No access token available");
      navigate("/auth/login");
      return;
    }
    if (isLoading) return;
    setIsLoading(true);
    try {
      const response = await api.get("/auth/sessions", {
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
      console.error("Failed to fetch sessions:", error.response?.data);
      const status = error.response?.status;
      const message =
        status === 401
          ? "Session expired. Logging out."
          : status === 500
            ? "Server error. Please try again later."
            : "Failed to load sessions.";
      toast.error(message);
      if (status === 401) {
        navigate("/auth/login");
      }
    } finally {
      setIsLoading(false);
    }
  }, [accessToken, navigate]);

  useEffect(() => {
    fetchSessions();
    const interval = setInterval(fetchSessions, 30000);
    return () => clearInterval(interval);
  }, [fetchSessions]);

  const handleRevoke = async (sessionId: string) => {
    if (isLoading) return;
    try {
      const result = await revokeSession(sessionId);
      if (result.success) {
        setSessions((prev) => prev.filter((s) => s.id !== sessionId));
        if (result.isCurrentSession) {
          navigate('/auth/login');
        }
      }
    } catch (error) {
      // Error handled in revokeSession
    }
  };

  const handleRevokeAll = async () => {
    if (isLoading) return;
    try {
      await revokeSession();
      const currentJti = accessToken
        ? jwtDecode<{ jti: string }>(accessToken).jti
        : "";
      setSessions((prev) => prev.filter((s) => s.id === currentJti));
    } catch (error) {
      // Error handled in revokeSession
    }
  };

  return (
    <div style={{ padding: "20px", fontFamily: "Arial, sans-serif" }}>
      <h2 style={{ fontSize: "20px", color: "#333", marginBottom: "10px" }}>
        Active Sessions
      </h2>
      {isLoading && sessions.length === 0 ? (
        <p style={{ color: "#666" }}>Loading sessions...</p>
      ) : sessions.length === 0 ? (
        <p style={{ color: "#666" }}>No active sessions</p>
      ) : (
        <ul style={{ listStyle: "none", padding: 0 }}>
          {sessions.map((session) => (
            <li
              key={session.id}
              style={{
                marginBottom: "15px",
                padding: "10px",
                border: "1px solid #ddd",
                borderRadius: "4px",
              }}
            >
              <p style={{ margin: "5px 0", color: "#333" }}>
                IP: {session.ip_address}
              </p>
              <p style={{ margin: "5px 0", color: "#333" }}>
                Device: {session.user_agent}
              </p>
              <p style={{ margin: "5px 0", color: "#333" }}>
                Created: {new Date(session.created_at).toLocaleString()}
              </p>
              <button
                onClick={() => handleRevoke(session.id)}
                disabled={isLoading}
                style={{
                  padding: "6px 12px",
                  backgroundColor: "#ffc107",
                  color: "#fff",
                  border: "none",
                  borderRadius: "4px",
                  cursor: isLoading ? "not-allowed" : "pointer",
                  opacity: isLoading ? 0.6 : 1,
                  fontSize: "14px",
                }}
                onMouseOver={(e) =>
                  (e.currentTarget.style.backgroundColor = "#e0a800")
                }
                onMouseOut={(e) =>
                  (e.currentTarget.style.backgroundColor = "#ffc107")
                }
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
        style={{
          marginTop: "20px",
          padding: "8px 16px",
          backgroundColor: "#fd7e14",
          color: "#fff",
          border: "none",
          borderRadius: "4px",
          cursor: isLoading ? "not-allowed" : "pointer",
          opacity: isLoading ? 0.6 : 1,
          fontSize: "14px",
        }}
        onMouseOver={(e) => (e.currentTarget.style.backgroundColor = "#e06c00")}
        onMouseOut={(e) => (e.currentTarget.style.backgroundColor = "#fd7e14")}
      >
        Revoke All Other Sessions
      </button>
    </div>
  );
};

export default Sessions;
