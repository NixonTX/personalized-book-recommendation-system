import { useContext, useEffect } from 'react';
import { AuthContext } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

export default function RefreshHandler() {
  const authContext = useContext(AuthContext);
  const navigate = useNavigate();

  useEffect(() => {
    if (!authContext || !authContext.isAuthenticated) {
      console.log('Skipping refresh handler:', {
        hasAuthContext: !!authContext,
        isAuthenticated: authContext?.isAuthenticated,
        user: authContext?.user,
      });
      return;
    }

    console.log('Running refresh handler, isAuthenticated:', authContext.isAuthenticated);

    const checkStatusInterval = setInterval(async () => {
      console.log('Checking auth status at', new Date().toISOString(), 'isAuthenticated:', authContext.isAuthenticated);
      try {
        const result = await authContext.checkAuthStatus();
        console.log('Interval check result:', result);
        if (!result.success && !result.isLoggedOut && result.error !== 'Rate limited') {
          console.log('Session invalid, redirecting to login', { result });
          navigate('/auth/login');
        } else if (result.error === 'Rate limited') {
          console.log('Skipping interval redirect: auth status check rate limited');
        }
      } catch (error: any) {
        console.error('Auth status check failed:', {
          message: error.message,
          status: error.response?.status,
          data: error.response?.data,
        });
        if (!error.isLoggedOut) {
          console.log('Redirecting to login due to error', { error });
          navigate('/auth/login');
        }
      }
    }, 15 * 60 * 1000); // Check every 15 minutes

    // Initial check on mount, delayed to avoid debounce
    const initialCheckTimeout = setTimeout(() => {
      checkAuthStatus();
    }, 1000); // Delay by 1 second

    async function checkAuthStatus() {
      if (!authContext) {
        console.log('Skipping checkAuthStatus: authContext is undefined');
        return;
      }
      console.log('checkAuthStatus called, isAuthenticated:', authContext.isAuthenticated, 'user:', authContext.user);
      try {
        const result = await authContext.checkAuthStatus();
        console.log('Initial check result:', result);
        if (!result.success && !result.isLoggedOut && result.error !== 'Rate limited') {
          console.log('Initial session check failed, redirecting to login', { result });
          navigate('/auth/login');
        } else if (result.error === 'Rate limited') {
          console.log('Skipping initial redirect: auth status check rate limited');
        }
      } catch (error: any) {
        console.error('Initial auth status check failed:', {
          message: error.message,
          status: error.response?.status,
          data: error.response?.data,
        });
        if (!error.isLoggedOut) {
          console.log('Initial check redirecting to login due to error', { error });
          navigate('/auth/login');
        }
      }
    }

    return () => {
      clearInterval(checkStatusInterval);
      clearTimeout(initialCheckTimeout);
    };
  }, [authContext, navigate]);

  return null;
}