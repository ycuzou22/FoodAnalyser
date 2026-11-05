import { afterEach, vi } from 'vitest';

import { API_URL, ApiError, apiFetch } from './client';

function mockFetch(status: number, body?: unknown): ReturnType<typeof vi.fn> {
  const fetchMock = vi.fn().mockResolvedValue(
    new Response(body === undefined ? null : JSON.stringify(body), {
      status,
      headers: { 'Content-Type': 'application/json' },
    }),
  );
  vi.stubGlobal('fetch', fetchMock);
  return fetchMock;
}

afterEach(() => {
  vi.unstubAllGlobals();
});

describe('apiFetch', () => {
  it('envoie le cookie de session et sérialise le corps en JSON', async () => {
    const fetchMock = mockFetch(200, { ok: true });

    await apiFetch('/api/v1/foods', { method: 'POST', body: { name: 'Banane' } });

    expect(fetchMock).toHaveBeenCalledWith(
      `${API_URL}/api/v1/foods`,
      expect.objectContaining({
        method: 'POST',
        credentials: 'include',
        body: '{"name":"Banane"}',
      }),
    );
  });

  it('transforme une réponse problem+json en ApiError avec son code métier', async () => {
    mockFetch(402, {
      type: 'https://foodanalyser.app/problems/free_quota_exceeded',
      title: 'Payment Required',
      status: 402,
      detail: 'Quota gratuit atteint.',
    });

    const error = await apiFetch('/x').catch((e: unknown) => e);

    expect(error).toBeInstanceOf(ApiError);
    expect((error as ApiError).status).toBe(402);
    expect((error as ApiError).code).toBe('free_quota_exceeded');
    expect((error as ApiError).message).toBe('Quota gratuit atteint.');
  });

  it('gère une erreur dont le corps n’est pas du JSON', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response('<html>', { status: 502 })));

    const error = (await apiFetch('/x').catch((e: unknown) => e)) as ApiError;

    expect(error.status).toBe(502);
    expect(error.code).toBeUndefined();
  });

  it('renvoie undefined pour une réponse 204', async () => {
    mockFetch(204);

    await expect(apiFetch('/x', { method: 'DELETE' })).resolves.toBeUndefined();
  });
});
