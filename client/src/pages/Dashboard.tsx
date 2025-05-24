import React, { useContext, useEffect, useState, useCallback } from 'react';
import { AuthContext } from '@/context/AuthContext';
import { toast } from 'react-toastify';
import api from '@/utils/api';
import { useNavigate } from 'react-router-dom';
import { SearchBar } from '@/components/search/SearchBar';
import debounce from 'lodash.debounce';

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
  name?: string;
  isbn?: string;
  title?: string;
  author?: string;
}

interface SearchMeta {
  total: number;
  page: number;
  per_page: number;
}

interface SearchResponse {
  results: Book[];
  meta: SearchMeta;
}

const Dashboard: React.FC = () => {
  const authContext = useContext(AuthContext);
  const navigate = useNavigate();
  const [sessions, setSessions] = useState<Session[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchLoading, setSearchLoading] = useState(false);
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [searchResults, setSearchResults] = useState<SearchResponse | null>(null);

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

  const fetchSuggestions = useCallback(async (value: string) => {
    if (value.length < 2) {
      setSuggestions([]);
      return;
    }
    setSearchLoading(true);
    try {
      const response = await api.get('/search/suggestions', {
        params: { q: value },
      });
      setSuggestions(response.data.suggestions || []);
    } catch (error: any) {
      console.error('Failed to fetch suggestions:', error.response?.data);
      const status = error.response?.status;
      const message = status === 400 ? 'Invalid suggestion query' :
                      status === 500 ? 'Server error fetching suggestions' :
                      status === 401 ? 'Session expired. Logging out.' :
                      'Failed to fetch suggestions';
      toast.error(message);
      if (status === 401) {
        logout();
        navigate('/auth/login');
      }
      setSuggestions([]);
    } finally {
      setSearchLoading(false);
    }
  }, [logout, navigate]);

  const debouncedFetchSuggestions = useCallback(
    debounce((value: string) => {
      fetchSuggestions(value);
    }, 300),
    [fetchSuggestions]
  );

  const handleSearchChange = useCallback((value: string) => {
    setSearchQuery(value); // Update input immediately
    debouncedFetchSuggestions(value); // Debounce only API call
  }, [debouncedFetchSuggestions]);

  const handleSearchSubmit = useCallback(async (query: string) => {
    if (!query || query.length < 2) {
      toast.error('Query must be at least 2 characters');
      return;
    }
    setSearchLoading(true);
    try {
      const response = await api.get('/search', {
        params: { q: query, page: 1, per_page: 10 },
      });
      console.log('Search response:', response.data);
      setSearchResults(response.data);
      if (response.data.meta.total === 0) {
        toast.info(`No books found for "${query}". Try a different spelling or keyword.`);
      } else {
        toast.success(`Found ${response.data.meta.total} book(s) for "${query}"`);
      }
    } catch (error: any) {
      console.error('Search failed:', error.response?.data);
      const status = error.response?.status;
      const message = status === 400 ? 'Invalid search query' :
                      status === 404 ? 'Search endpoint not found' :
                      status === 500 ? 'Server error during search' :
                      status === 401 ? 'Session expired. Logging out.' :
                      'Failed to search books';
      toast.error(message);
      if (status === 401) {
        logout();
        navigate('/auth/login');
      }
      setSearchResults(null);
    } finally {
      setSearchLoading(false);
    }
  }, [logout, navigate]);

  const handleSuggestionSelect = useCallback((suggestion: Suggestion) => {
    const query = suggestion.title || suggestion.name || '';
    setSearchQuery(query);
    setSuggestions([]);
    if (query) {
      handleSearchSubmit(query);
    }
  }, [handleSearchSubmit]);

  const handleSearchClear = useCallback(() => {
    setSearchQuery('');
    setSuggestions([]);
    setSearchResults(null);
    debouncedFetchSuggestions.cancel();
  }, [debouncedFetchSuggestions]);

  useEffect(() => {
    fetchSessions();
    const interval = setInterval(fetchSessions, 30000);
    return () => clearInterval(interval);
  }, [fetchSessions]);

  useEffect(() => {
    return () => {
      debouncedFetchSuggestions.cancel(); // Cleanup debounce on unmount
    };
  }, [debouncedFetchSuggestions]);

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
          {searchLoading && (
            <p style={{ textAlign: 'center', color: '#666', marginTop: '10px' }}>
              Loading...
            </p>
          )}
          {searchResults && (
            <div style={{ marginTop: '20px' }}>
              <p style={{ color: '#333', fontSize: '16px', marginBottom: '10px' }}>
                {searchResults.meta.total > 0
                  ? `Found ${searchResults.meta.total} result${searchResults.meta.total === 1 ? '' : 's'}`
                  : 'No results found'}
              </p>
              {searchResults.meta.total > 0 && (
                <ul style={{ listStyle: 'none', padding: 0 }}>
                  {searchResults.results.map((book) => (
                    <li
                      key={book.isbn}
                      style={{
                        padding: '10px',
                        borderBottom: '1px solid #eee',
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                      }}
                    >
                      <div>
                        <span style={{ fontWeight: 'bold', color: '#333' }}>{book.title}</span>
                        <span style={{ color: '#666', marginLeft: '10px' }}>by {book.author}</span>
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;