import { onlineManager } from '@tanstack/react-query';
import { act, fireEvent, render, renderHook, screen } from '@testing-library/react-native';
import * as SecureStore from 'expo-secure-store';
import * as ReactNative from 'react-native';

import { App } from './App';
import { ErrorBoundary } from './components/ErrorBoundary';
import { useSession } from './store/session';
import { secureTokenStorage } from './store/tokenStorage';
import { buildTheme, useTheme } from './theme/useTheme';

beforeEach(() => {
  (SecureStore as unknown as { resetMock: () => void }).resetMock();
  useSession.setState({ status: 'loading' });
  onlineManager.setOnline(true);
});

describe('App', () => {
  it('affiche l’accueil quand l’utilisateur n’est pas connecté', async () => {
    await render(<App />);

    expect(await screen.findByText('FoodAnalyser')).toBeOnTheScreen();
    expect(screen.queryByText('Journal')).not.toBeOnTheScreen();
  });

  it('ouvre le journal et les cinq onglets quand une session existe', async () => {
    await secureTokenStorage.save({ accessToken: 'a1', refreshToken: 'r1' });

    await render(<App />);

    expect(await screen.findByText('Journal du jour')).toBeOnTheScreen();
    for (const label of ['Journal', 'Statistiques', 'Recettes', 'Profil']) {
      expect(screen.getByText(label)).toBeOnTheScreen();
    }
    // Onglet central sans libellé visible, mais annoncé au lecteur d'écran.
    expect(screen.getByLabelText('Photographier un repas')).toBeOnTheScreen();
  });

  it('ouvre l’écran photo depuis le bouton central', async () => {
    await secureTokenStorage.save({ accessToken: 'a1', refreshToken: 'r1' });
    await render(<App />);
    await screen.findByText('Journal du jour');

    await fireEvent.press(screen.getByLabelText('Photographier un repas'));

    expect(await screen.findByText("Arrive avec l'issue #24")).toBeOnTheScreen();
  });

  it('affiche un bandeau hors ligne', async () => {
    await render(<App />);
    await screen.findByText('FoodAnalyser');

    await act(() => onlineManager.setOnline(false));

    expect(screen.getByText(/Hors ligne/)).toBeOnTheScreen();
  });
});

describe('ErrorBoundary', () => {
  function Broken(): never {
    throw new Error('panne');
  }

  it('remplace un écran qui plante par un écran d’erreur', async () => {
    jest.spyOn(console, 'error').mockImplementation(() => undefined);

    await render(
      <ErrorBoundary>
        <Broken />
      </ErrorBoundary>,
    );

    expect(screen.getByText('Une erreur est survenue')).toBeOnTheScreen();
    expect(screen.getByRole('button', { name: 'Réessayer' })).toBeOnTheScreen();
  });
});

describe('thème', () => {
  it('fournit une palette sombre distincte de la claire', () => {
    const light = buildTheme('light');
    const dark = buildTheme('dark');

    expect(dark.colors.background).not.toEqual(light.colors.background);
    expect(dark.navigation.dark).toBe(true);
    expect(light.navigation.colors.primary).toBe(light.colors.primary);
  });

  it('suit le réglage clair / sombre du téléphone', async () => {
    const spy = jest.spyOn(ReactNative, 'useColorScheme').mockReturnValue('dark');
    const { result, rerender } = await renderHook(() => useTheme());
    expect(result.current.scheme).toBe('dark');

    spy.mockReturnValue('light');
    await rerender({});
    expect(result.current.scheme).toBe('light');
    spy.mockRestore();
  });
});
