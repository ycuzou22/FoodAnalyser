import type { TokenStorage, Tokens } from '../store/tokenStorage';

/** Corps d'erreur RFC 9457 renvoyé par l'API. */
export interface Problem {
  type: string;
  title: string;
  status: number;
  detail?: string;
  request_id?: string;
  [extension: string]: unknown;
}

export class ApiError extends Error {
  readonly status: number;
  readonly problem: Problem;

  constructor(problem: Problem) {
    super(problem.detail ?? problem.title);
    this.name = 'ApiError';
    this.status = problem.status;
    this.problem = problem;
  }

  /** Code métier stable (dernier segment de `type`), ex. `free_quota_exceeded`. */
  get code(): string | undefined {
    return this.problem.type === 'about:blank' ? undefined : this.problem.type.split('/').pop();
  }
}

export interface ApiClientOptions {
  baseUrl: string;
  storage: TokenStorage;
  /** Appelé quand le refresh token est refusé : la session est terminée. */
  onSessionExpired: () => void;
  fetchImpl?: typeof fetch;
}

export interface RequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
  body?: unknown;
  /** Route publique (connexion, inscription) : pas de jeton envoyé. */
  anonymous?: boolean;
}

const REFRESH_PATH = '/api/v1/auth/refresh';

function isProblem(value: unknown): value is Problem {
  return (
    typeof value === 'object' &&
    value !== null &&
    typeof (value as Problem).status === 'number' &&
    typeof (value as Problem).title === 'string'
  );
}

/**
 * Client HTTP de l'application.
 *
 * - Ajoute le jeton d'accès à chaque requête authentifiée.
 * - Sur un 401, rafraîchit la session **une seule fois** même si plusieurs requêtes échouent
 *   en même temps (le refresh token est rotatif : deux rafraîchissements parallèles
 *   révoqueraient toute la session côté API), puis rejoue la requête.
 * - Si le rafraîchissement échoue, efface les jetons et signale la fin de session.
 */
export function createApiClient({
  baseUrl,
  storage,
  onSessionExpired,
  fetchImpl = fetch,
}: ApiClientOptions) {
  let refreshInFlight: Promise<Tokens | null> | null = null;

  async function send(path: string, options: RequestOptions, accessToken?: string) {
    const headers: Record<string, string> = { Accept: 'application/json' };
    if (options.body !== undefined) headers['Content-Type'] = 'application/json';
    if (accessToken) headers.Authorization = `Bearer ${accessToken}`;
    return fetchImpl(`${baseUrl}${path}`, {
      method: options.method ?? 'GET',
      headers,
      ...(options.body === undefined ? {} : { body: JSON.stringify(options.body) }),
    });
  }

  async function refresh(): Promise<Tokens | null> {
    const current = await storage.load();
    if (!current) return null;
    const response = await send(REFRESH_PATH, {
      method: 'POST',
      body: { refresh_token: current.refreshToken },
    });
    if (!response.ok) return null;
    const body = (await response.json()) as { access_token: string; refresh_token: string };
    const tokens = { accessToken: body.access_token, refreshToken: body.refresh_token };
    await storage.save(tokens);
    return tokens;
  }

  function refreshOnce(): Promise<Tokens | null> {
    refreshInFlight ??= refresh()
      .catch(() => null)
      .finally(() => {
        refreshInFlight = null;
      });
    return refreshInFlight;
  }

  async function parse<T>(response: Response): Promise<T> {
    if (response.status === 204) return undefined as T;
    const payload: unknown = await response.json().catch(() => undefined);
    if (!response.ok) {
      throw new ApiError(
        isProblem(payload)
          ? payload
          : { type: 'about:blank', title: `HTTP ${response.status}`, status: response.status },
      );
    }
    return payload as T;
  }

  async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
    if (options.anonymous) return parse<T>(await send(path, options));

    const tokens = await storage.load();
    let response = await send(path, options, tokens?.accessToken);
    if (response.status === 401) {
      const renewed = await refreshOnce();
      if (!renewed) {
        await storage.clear();
        onSessionExpired();
        return parse<T>(response);
      }
      response = await send(path, options, renewed.accessToken);
    }
    return parse<T>(response);
  }

  return { request };
}

export type ApiClient = ReturnType<typeof createApiClient>;
