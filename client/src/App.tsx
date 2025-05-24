// L2/client/src/App.tsx
import { Outlet } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

export default function App() {
  return (
    <>
      <ToastContainer position="top-right" autoClose={3000} />
      <Outlet />
    </>
  );
}