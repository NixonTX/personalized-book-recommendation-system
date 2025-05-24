import { useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '../../context/AuthContext';

export default function LogoutPage() {
  const authContext = useContext(AuthContext);
  const navigate = useNavigate();

  useEffect(() => {
    const performLogout = async () => {
      if (authContext) {
         const result = await authContext.logout();
         if(result.success) {
          navigate('/auth/login');
         }        
      }
    };

    performLogout();
  }, [authContext, navigate]);

  return (
    <div className="text-center py-12">
      <p className="text-lg">Signing out...</p>
    </div>
  );
}