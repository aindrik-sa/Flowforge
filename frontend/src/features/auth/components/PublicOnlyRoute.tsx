import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

export function PublicOnlyRoute() {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div style={{ height: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <p className="text-secondary">Loading FlowForge...</p>
      </div>
    );
  }

  // If user is already logged in, send them to the dashboard
  if (user) {
    return <Navigate to="/" replace />;
  }

  return <Outlet />;
}
