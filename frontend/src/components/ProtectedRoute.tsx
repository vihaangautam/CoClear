import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Loader2 } from 'lucide-react';

export default function ProtectedRoute() {
  const { operator, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <div className="auth-loading">
        <Loader2 className="spinner" size={32} />
      </div>
    );
  }

  if (!operator) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  return <Outlet />;
}