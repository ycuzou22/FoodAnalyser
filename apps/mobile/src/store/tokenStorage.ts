import * as SecureStore from 'expo-secure-store';

/**
 * Stockage des jetons dans le Keychain (iOS) ou le Keystore (Android), jamais dans
 * AsyncStorage (fichier en clair). `WHEN_UNLOCKED_THIS_DEVICE_ONLY` : lisible seulement
 * quand le téléphone est déverrouillé, et jamais restauré sur un autre appareil.
 */

export interface Tokens {
  accessToken: string;
  refreshToken: string;
}

export interface TokenStorage {
  load(): Promise<Tokens | null>;
  save(tokens: Tokens): Promise<void>;
  clear(): Promise<void>;
}

const ACCESS_KEY = 'foodanalyser.access_token';
const REFRESH_KEY = 'foodanalyser.refresh_token';
const OPTIONS: SecureStore.SecureStoreOptions = {
  keychainAccessible: SecureStore.WHEN_UNLOCKED_THIS_DEVICE_ONLY,
};

export const secureTokenStorage: TokenStorage = {
  async load() {
    const [accessToken, refreshToken] = await Promise.all([
      SecureStore.getItemAsync(ACCESS_KEY, OPTIONS),
      SecureStore.getItemAsync(REFRESH_KEY, OPTIONS),
    ]);
    return accessToken && refreshToken ? { accessToken, refreshToken } : null;
  },
  async save(tokens) {
    await Promise.all([
      SecureStore.setItemAsync(ACCESS_KEY, tokens.accessToken, OPTIONS),
      SecureStore.setItemAsync(REFRESH_KEY, tokens.refreshToken, OPTIONS),
    ]);
  },
  async clear() {
    await Promise.all([
      SecureStore.deleteItemAsync(ACCESS_KEY, OPTIONS),
      SecureStore.deleteItemAsync(REFRESH_KEY, OPTIONS),
    ]);
  },
};
