import type { ReactNode } from 'react';
import { Navigate, useLocation } from 'react-router';

import { useAuth } from './auth';

/** Redirige vers /login toute route protégée tant qu'aucun administrateur n'est connecté. */
export function RequireAuth({ children }: { children: ReactNode }) {
  const { user } = useAuth();
  const location = useLocation();

  if (user === null) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }
  return children;
}
