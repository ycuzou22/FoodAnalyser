/**
 * Client HTTP du back-office.
 *
 * L'authentification administrateur repose sur un cookie de session `HttpOnly` posé par l'API
 * (issue #34) : aucun jeton n'est stocké en JavaScript, donc rien à voler par une faille XSS.
 */

export const API_URL: string = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

/** Corps d'erreur RFC 9457 renvoyé par l'API. */
export interface Problem {
  type: string;
  title: string;
  status: number;
  detail?: string;
  instance?: string;
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

export interface RequestOptions extends Omit<RequestInit, 'body'> {
  body?: unknown;
}

function isProblem(value: unknown): value is Problem {
  return (
    typeof value === 'object' &&
    value !== null &&
    typeof (value as Problem).status === 'number' &&
    typeof (value as Problem).title === 'string'
  );
}

export async function apiFetch<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { body, headers, ...init } = options;
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    credentials: 'include',
    headers: {
      Accept: 'application/json, application/problem+json',
      ...(body === undefined ? {} : { 'Content-Type': 'application/json' }),
      ...headers,
    },
    ...(body === undefined ? {} : { body: JSON.stringify(body) }),
  });

  if (response.status === 204) {
    return undefined as T;
  }

  const payload: unknown = await response.json().catch(() => undefined);
  if (!response.ok) {
    throw new ApiError(
      isProblem(payload)
        ? payload
        : { type: 'about:blank', title: response.statusText, status: response.status },
    );
  }
  return payload as T;
}
