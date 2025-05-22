import { useContext } from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import RefreshHandler from './RefreshHandler';

// export default function ProtectedRoutes() {
//   const authContext = useContext(AuthContext);

//   if (!authContext) {
//     return <Navigate to="/login" replace />;
//   }

//   return authContext.isAuthenticated ? <Outlet /> : <Navigate to="/login" replace />;
// }

const ProtectedRoutes: React.FC = () => {
  const authContext = useContext(AuthContext);

  if(!authContext) {
    throw new Error('AuthContext must be used within AuthProvider');
  }

  const { isAuthenticated } = authContext;

  if (!isAuthenticated) {
    return <Navigate to="/auth/login" replace />;
  }

  return (
    <>
      <RefreshHandler />
      <Outlet />
    </>
  );
}

export default ProtectedRoutes;