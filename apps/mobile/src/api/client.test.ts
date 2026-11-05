import type { TokenStorage, Tokens } from '../store/tokenStorage';
import { ApiError, createApiClient } from './client';

function memoryStorage(initial: Tokens | null): TokenStorage & { current: Tokens | null } {
  const storage = {
    current: initial,
    load: async () => storage.current,
    save: async (tokens: Tokens) => {
      storage.current = tokens;
    },
    clear: async () => {
      storage.current = null;
    },
  };
  return storage;
}

function json(status: number, body?: unknown): Response {
  return new Response(body === undefined ? null : JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}

const BASE = 'https://api.test';

describe('createApiClient', () => {
  it('envoie le jeton d’accès dans l’en-tête Authorization', async () => {
    const fetchImpl = jest.fn().mockResolvedValue(json(200, { ok: true }));
    const client = createApiClient({
      baseUrl: BASE,
      storage: memoryStorage({ accessToken: 'a1', refreshToken: 'r1' }),
      onSessionExpired: jest.fn(),
      fetchImpl,
    });

    await client.request('/api/v1/journal/2026-11-05');

    expect(fetchImpl).toHaveBeenCalledWith(
      `${BASE}/api/v1/journal/2026-11-05`,
      expect.objectContaining({ headers: expect.objectContaining({ Authorization: 'Bearer a1' }) }),
    );
  });

  it('n’envoie aucun jeton sur une route publique', async () => {
    const fetchImpl = jest.fn().mockResolvedValue(json(200, {}));
    const client = createApiClient({
      baseUrl: BASE,
      storage: memoryStorage({ accessToken: 'a1', refreshToken: 'r1' }),
      onSessionExpired: jest.fn(),
      fetchImpl,
    });

    await client.request('/api/v1/auth/login', { method: 'POST', body: {}, anonymous: true });

    const headers = (fetchImpl.mock.calls[0]?.[1] as RequestInit).headers as Record<string, string>;
    expect(headers.Authorization).toBeUndefined();
  });

  it('rafraîchit une seule fois pour des 401 simultanés, puis rejoue chaque requête', async () => {
    const storage = memoryStorage({ accessToken: 'expired', refreshToken: 'r1' });
    const fetchImpl = jest.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.endsWith('/auth/refresh')) {
        return json(200, { access_token: 'a2', refresh_token: 'r2' });
      }
      const auth = (init?.headers as Record<string, string>).Authorization;
      return auth === 'Bearer a2'
        ? json(200, { url })
        : json(401, { title: 'Unauthorized', status: 401, type: 'about:blank' });
    });
    const client = createApiClient({
      baseUrl: BASE,
      storage,
      onSessionExpired: jest.fn(),
      fetchImpl,
    });

    const results = await Promise.all([
      client.request('/a'),
      client.request('/b'),
      client.request('/c'),
    ]);

    const refreshCalls = fetchImpl.mock.calls.filter(([input]) =>
      String(input).endsWith('/auth/refresh'),
    );
    expect(refreshCalls).toHaveLength(1);
    expect(results).toEqual([{ url: `${BASE}/a` }, { url: `${BASE}/b` }, { url: `${BASE}/c` }]);
    expect(storage.current).toEqual({ accessToken: 'a2', refreshToken: 'r2' });
  });

  it('termine la session si le refresh token est refusé', async () => {
    const storage = memoryStorage({ accessToken: 'expired', refreshToken: 'revoked' });
    const onSessionExpired = jest.fn();
    // L'accès comme le rafraîchissement sont refusés.
    const fetchImpl = jest.fn<Promise<Response>, [RequestInfo | URL, RequestInit?]>(async () =>
      json(401, { title: 'Unauthorized', status: 401, type: 'about:blank' }),
    );
    const client = createApiClient({ baseUrl: BASE, storage, onSessionExpired, fetchImpl });

    await expect(client.request('/a')).rejects.toBeInstanceOf(ApiError);
    expect(onSessionExpired).toHaveBeenCalledTimes(1);
    expect(storage.current).toBeNull();
  });

  it('transforme une erreur problem+json en ApiError avec son code métier', async () => {
    const fetchImpl = jest.fn().mockResolvedValue(
      json(402, {
        type: 'https://foodanalyser.app/problems/free_quota_exceeded',
        title: 'Payment Required',
        status: 402,
        detail: 'Quota gratuit atteint.',
      }),
    );
    const client = createApiClient({
      baseUrl: BASE,
      storage: memoryStorage({ accessToken: 'a', refreshToken: 'r' }),
      onSessionExpired: jest.fn(),
      fetchImpl,
    });

    const error = (await client.request('/x').catch((e: unknown) => e)) as ApiError;

    expect(error.status).toBe(402);
    expect(error.code).toBe('free_quota_exceeded');
    expect(error.message).toBe('Quota gratuit atteint.');
  });
});
