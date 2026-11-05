import '@mantine/core/styles.css';

import { MantineProvider } from '@mantine/core';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useState, type ReactNode } from 'react';

import { ApiError } from '../api/client';
import type { AdminUser } from '../features/auth/auth';
import { AuthProvider } from '../features/auth/AuthProvider';
import { theme } from './theme';

function createQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 30_000,
        // Inutile de réessayer une erreur client (401, 403, 404, 422) : elle se reproduira.
        retry: (failureCount, error) =>
          !(error instanceof ApiError && error.status < 500) && failureCount < 2,
      },
    },
  });
}

export function Providers({
  children,
  initialUser = null,
}: {
  children: ReactNode;
  initialUser?: AdminUser | null;
}) {
  const [queryClient] = useState(createQueryClient);
  return (
    <MantineProvider theme={theme} defaultColorScheme="auto">
      <QueryClientProvider client={queryClient}>
        <AuthProvider initialUser={initialUser}>{children}</AuthProvider>
      </QueryClientProvider>
    </MantineProvider>
  );
}
