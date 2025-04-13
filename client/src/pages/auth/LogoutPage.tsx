import { useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '../../context/AuthContext';

export default function LogoutPage() {
  const navigate = useNavigate();
  const authContext = useContext(AuthContext);

  useEffect(() => {
    const performLogout = async () => {
      if (authContext) {
        await authContext.logout();
      }
    };

    performLogout();
  }, [authContext]);

  return (
    <div className="text-center py-12">
      <p className="text-lg">Signing out...</p>
    </div>
  );
}