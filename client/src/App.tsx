// L2/client/src/App.tsx
// Replace entire file (lines 1–30)
import { Routes, Route } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { AuthProvider } from './context/AuthContext';
import AuthLayout from './pages/auth/AuthLayout';
import LoginPage from './pages/auth/LoginPage';
import RegisterPage from './pages/auth/RegisterPage';
import LogoutPage from './pages/auth/LogoutPage';
import VerifyEmailPage from './pages/auth/VerifyEmailPage';
import HomePage from './pages/HomePage';
import ProtectedRoutes from './pages/ProtectedRoutes';
import RefreshHandler from './pages/RefreshHandler';
import Dashboard from './pages/Dashboard';

export default function App() {
  return (
    <AuthProvider>
      <RefreshHandler />
      <ToastContainer position="top-right" autoClose={3000} />
      <Routes>
        <Route element={<AuthLayout />}>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/logout" element={<LogoutPage />} />
          <Route path="/verify-email/:token" element={<VerifyEmailPage />} />
        </Route>
        <Route element={<ProtectedRoutes />}>
          <Route path="/dashboard" element={<Dashboard />} />
        </Route>
        <Route path="/" element={<HomePage />} />
      </Routes>
    </AuthProvider>
  );
}