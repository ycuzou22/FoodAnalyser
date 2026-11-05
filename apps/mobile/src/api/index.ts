import { useSession } from '../store/session';
import { secureTokenStorage } from '../store/tokenStorage';
import { createApiClient } from './client';

/** URL de l'API selon l'environnement (fichier .env.local, variables EXPO_PUBLIC_*). */
export const API_URL = process.env.EXPO_PUBLIC_API_URL ?? 'http://localhost:8000';

export const api = createApiClient({
  baseUrl: API_URL,
  storage: secureTokenStorage,
  onSessionExpired: () => {
    void useSession.getState().signOut();
  },
});

export { ApiError } from './client';
