import React, { useContext, useEffect, useState, useCallback } from 'react';
import { AuthContext } from '../context/AuthContext';
import { toast } from 'react-toastify';
import api from '../utils/api';
import { useNavigate } from 'react-router-dom';
import { SearchBar } from '../components/search/SearchBar';

interface Session {
  id: string;
  ip_address: string;
  user_agent: string;
  created_at: string;
}

interface Book {
  isbn: string;
  title: string;
  author: string;
}

interface Suggestion {
  name: string;
}

const Dashboard: React.FC = () => {
  const authContext = useContext(AuthContext);
  const navigate = useNavigate();
  const [sessions, setSessions] = useState<Session[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchLoading, setSearchLoading] = useState(false);
  const [suggestions, setSuggestions] = useState<(Book | Suggestion)[]>([]);


  if (!authContext) {
    throw new Error('AuthContext must be used within AuthProvider');
  }

  const { user, logout } = authContext;

  const fetchSessions = useCallback(async () => {
    if (isLoading) return;
    setIsLoading(true);
    try {
      const response = await api.get('/auth/sessions');
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
  }, [logout, navigate]);

  const handleSearchSubmit = useCallback(async (query: string) => {
    if (!query) return;
    setSearchLoading(true);
    try {
      const response = await api.post('/search/books', { query });
      const { books } = response.data;
      toast.success(`Found ${books.length} book(s) for "${query}"`);
      // Optionally navigate to a results page or display results
      // navigate(`/search?query=${encodeURIComponent(query)}`);
    } catch (error: any) {
      console.error('Search failed:', error.response?.data);
      const message = error.response?.status === 400 ? 'Invalid search query' :
                      error.response?.status === 500 ? 'Server error during search' :
                      'Failed to search books';
      toast.error(message);
    } finally {
      setSearchLoading(false);
    }
  }, []);

  const handleSearchChange = useCallback(async (value: string) => {
    setSearchQuery(value);
    if (value.length < 2) {
      setSuggestions([]);
      return;
    }
    setSearchLoading(true);
    try {
      const response = await api.post('/search/books', { query: value });
      setSuggestions(response.data.suggestions || []);
    } catch (error: any) {
      console.error('Failed to fetch suggestions:', error.response?.data);
      setSuggestions([]);
    } finally {
      setSearchLoading(false);
    }
  }, []);

  const handleSuggestionSelect = useCallback((suggestion: Book | Suggestion) => {
    const query = 'isbn' in suggestion ? suggestion.title : suggestion.name;
    setSearchQuery(query);
    handleSearchSubmit(query);
  }, [handleSearchSubmit]);

  const handleSearchClear = useCallback(() => {
    setSearchQuery('');
    setSuggestions([]);
  }, []);

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
      <div style={{ display: 'flex', justifyContent: 'center', margin: '40px 0' }}>
        <div style={{ width: '100%', maxWidth: '600px' }}>
          <h2 style={{ fontSize: '20px', color: '#333', marginBottom: '10px', textAlign: 'center' }}>
            Search Books
          </h2>
          <SearchBar
            value={searchQuery}
            onChange={handleSearchChange}
            onSubmit={handleSearchSubmit}
            onClear={handleSearchClear}
            loading={searchLoading}
            placeholder="Search books or authors"
            suggestions={suggestions}
            onSuggestionsSelect={handleSuggestionSelect}
          />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;