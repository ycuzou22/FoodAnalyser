import { render, type RenderResult } from '@testing-library/react';
import { MemoryRouter } from 'react-router';

import { AppRoutes } from '../app/AppRoutes';
import { Providers } from '../app/Providers';
import type { AdminUser } from '../features/auth/auth';

export const ADMIN: AdminUser = { id: 'admin-1', email: 'admin@example.test', roles: ['admin'] };

export function renderApp(path: string, user: AdminUser | null = ADMIN): RenderResult {
  return render(
    <Providers initialUser={user}>
      <MemoryRouter initialEntries={[path]}>
        <AppRoutes />
      </MemoryRouter>
    </Providers>,
  );
}
