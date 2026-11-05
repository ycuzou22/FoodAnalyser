import { useMemo, useState, type ReactNode } from 'react';

import { AuthContext, type AdminUser } from './auth';

/**
 * État d'authentification du back-office.
 *
 * Pour l'instant l'utilisateur est fourni par l'appelant (tests, futur appel `GET /admin/me`).
 * La connexion avec MFA et la vérification des rôles côté API arrivent avec l'issue #34 ;
 * le contrôle d'accès réel est toujours fait par l'API, jamais seulement ici.
 */
export function AuthProvider({
  children,
  initialUser = null,
}: {
  children: ReactNode;
  initialUser?: AdminUser | null;
}) {
  const [user, setUser] = useState<AdminUser | null>(initialUser);
  const value = useMemo(() => ({ user, setUser }), [user]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
