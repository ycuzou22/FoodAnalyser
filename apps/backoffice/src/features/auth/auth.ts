import { createContext, useContext } from 'react';

export type AdminRole = 'admin' | 'nutrition_editor' | 'content_editor' | 'analyst';

export interface AdminUser {
  id: string;
  email: string;
  roles: AdminRole[];
}

export interface AuthState {
  user: AdminUser | null;
  setUser: (user: AdminUser | null) => void;
}

export const AuthContext = createContext<AuthState | null>(null);

export function useAuth(): AuthState {
  const context = useContext(AuthContext);
  if (context === null) {
    throw new Error('useAuth doit être utilisé dans un <AuthProvider>');
  }
  return context;
}
