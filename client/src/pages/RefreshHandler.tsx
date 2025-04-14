import { useContext, useEffect } from 'react';
import { AuthContext } from '../context/AuthContext';

export default function RefreshHandler() {
  const authContext = useContext(AuthContext);

  useEffect(() => {
    if (!authContext || !authContext.isAuthenticated) return;

    const refreshInterval = setInterval(async () => {
      console.log('Attempting token refresh at', new Date().toISOString());
      try {
        await authContext.refresh();
        console.log('Token refresh successful');
      } catch (error: any) {
        console.error('Token refresh failed:', {
          message: error.message,
          status: error.response?.status,
          data: error.response?.data
        });
        authContext.logout();
      }
    }, 13 * 60 * 1000); // Refresh every 13 minutes

    return () => clearInterval(refreshInterval);
  }, [authContext]);

  return null;
}