import type { AdminRole } from '../features/auth/auth';

export interface NavigationItem {
  path: string;
  label: string;
  /** Rôles qui voient l'entrée. L'API vérifie de nouveau les droits à chaque appel. */
  roles: AdminRole[];
}

export const NAVIGATION: NavigationItem[] = [
  { path: '/foods', label: 'Aliments', roles: ['admin', 'nutrition_editor'] },
  { path: '/moderation', label: 'Modération', roles: ['admin', 'nutrition_editor'] },
  { path: '/content', label: 'Contenus', roles: ['admin', 'content_editor'] },
  { path: '/dashboard', label: 'Tableau de bord', roles: ['admin', 'analyst'] },
  { path: '/users', label: 'Utilisateurs', roles: ['admin'] },
];

export function visibleNavigation(roles: AdminRole[]): NavigationItem[] {
  return NAVIGATION.filter((item) => item.roles.some((role) => roles.includes(role)));
}
