import { Navigate, useLocation } from 'react-router-dom';
import { getToken } from '@/services/api';
import type { ReactNode } from 'react';

export function AuthGuard({ children }: { children: ReactNode }) {
  const location = useLocation();
  const isAuthenticated = !!getToken();

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return <>{children}</>;
}
