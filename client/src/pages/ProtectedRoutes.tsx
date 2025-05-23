import { useContext, useEffect } from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import RefreshHandler from './RefreshHandler';

const ProtectedRoutes: React.FC = () => {
  const authContext = useContext(AuthContext);

  if (!authContext) {
    throw new Error('AuthContext must be used within AuthProvider');
  }

  const { isAuthenticated, user } = authContext;

  useEffect(() => {
    console.log(`ProtectedRoutes: Checking auth status at ${new Date().toISOString()}`, {
      isAuthenticated,
      user,
    });
    const timer = setTimeout(() => {
      if (!isAuthenticated) {
        console.log('ProtectedRoutes: Not authenticated, redirecting to login');
        // Navigate is handled in render to avoid multiple redirects
      }
    }, 500); // Wait 500ms for state to settle
    return () => clearTimeout(timer);
  }, [isAuthenticated, user]);

  if (!isAuthenticated) {
    console.log('ProtectedRoutes: Rendering redirect to /auth/login');
    return <Navigate to="/auth/login" replace />;
  }

  return (
    <>
      <RefreshHandler />
      <Outlet />
    </>
  );
};

export default ProtectedRoutes;