import { useEffect, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';

export default function RefreshHandler() {
  const authContext = useContext(AuthContext);

  useEffect(() => {
    if (!authContext || !authContext.isAuthenticated) return;

    const refreshInterval = setInterval(async () => {
      try {
        await authContext.refresh();
      } catch (error) {
        // Redirect handled in AuthContext
      }
    }, 10 * 60 * 1000); // Refresh every 10 minutes

    return () => clearInterval(refreshInterval);
  }, [authContext]);

  return null;
}