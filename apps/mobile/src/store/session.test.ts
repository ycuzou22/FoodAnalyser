import * as SecureStore from 'expo-secure-store';

import { createSessionStore } from './session';
import { secureTokenStorage } from './tokenStorage';

beforeEach(() => {
  (SecureStore as unknown as { resetMock: () => void }).resetMock();
  jest.clearAllMocks();
});

describe('session', () => {
  it('démarre déconnectée quand aucun jeton n’est enregistré', async () => {
    const store = createSessionStore();

    await store.getState().restore();

    expect(store.getState().status).toBe('signedOut');
  });

  it('enregistre les jetons dans le stockage sécurisé, accessibles sur cet appareil seulement', async () => {
    const store = createSessionStore();

    await store.getState().signIn({ accessToken: 'a1', refreshToken: 'r1' });

    expect(store.getState().status).toBe('signedIn');
    expect(SecureStore.setItemAsync).toHaveBeenCalledWith(
      'foodanalyser.refresh_token',
      'r1',
      expect.objectContaining({ keychainAccessible: SecureStore.WHEN_UNLOCKED_THIS_DEVICE_ONLY }),
    );
    expect(await secureTokenStorage.load()).toEqual({ accessToken: 'a1', refreshToken: 'r1' });
  });

  it('restaure une session existante au démarrage', async () => {
    await secureTokenStorage.save({ accessToken: 'a1', refreshToken: 'r1' });
    const store = createSessionStore();

    await store.getState().restore();

    expect(store.getState().status).toBe('signedIn');
  });

  it('efface les jetons à la déconnexion', async () => {
    const store = createSessionStore();
    await store.getState().signIn({ accessToken: 'a1', refreshToken: 'r1' });

    await store.getState().signOut();

    expect(store.getState().status).toBe('signedOut');
    expect(await secureTokenStorage.load()).toBeNull();
  });

  it('considère la session fermée si le stockage sécurisé est illisible', async () => {
    const store = createSessionStore({
      load: () => Promise.reject(new Error('Keychain verrouillé')),
      save: jest.fn(),
      clear: jest.fn(),
    });

    await store.getState().restore();

    expect(store.getState().status).toBe('signedOut');
  });
});
