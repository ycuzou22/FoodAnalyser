import { create } from 'zustand';

import { secureTokenStorage, type TokenStorage, type Tokens } from './tokenStorage';

export type SessionStatus = 'loading' | 'signedOut' | 'signedIn';

interface SessionState {
  status: SessionStatus;
  /** Lit les jetons au démarrage pour choisir l'écran d'accueil. */
  restore: () => Promise<void>;
  signIn: (tokens: Tokens) => Promise<void>;
  signOut: () => Promise<void>;
}

export function createSessionStore(storage: TokenStorage = secureTokenStorage) {
  return create<SessionState>()((set) => ({
    status: 'loading',
    restore: async () => {
      const tokens = await storage.load().catch(() => null);
      set({ status: tokens ? 'signedIn' : 'signedOut' });
    },
    signIn: async (tokens) => {
      await storage.save(tokens);
      set({ status: 'signedIn' });
    },
    signOut: async () => {
      await storage.clear();
      set({ status: 'signedOut' });
    },
  }));
}

export const useSession = createSessionStore();
