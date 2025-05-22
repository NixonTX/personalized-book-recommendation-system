import { useContext, useEffect } from 'react';
import { AuthContext } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

export default function RefreshHandler() {
  const authContext = useContext(AuthContext);
  const navigate = useNavigate();

  useEffect(() => {
    if (!authContext || !authContext.isAuthenticated) return;

    const refreshInterval = setInterval(async () => {
      console.log('Attempting token refresh at', new Date().toISOString());
      try {
        const result = await authContext.refresh();
        if (!result.success) {
          navigate('/auth/login');
        }
        console.log('Token refresh successful');
      } catch (error: any) {
        console.error('Token refresh failed:', {
          message: error.message,
          status: error.response?.status,
          data: error.response?.data
        });
        navigate('/auth/login');
      }
    }, 13 * 60 * 1000); // Refresh every 13 minutes

    return () => clearInterval(refreshInterval);
  }, [authContext]);

  return null;
}