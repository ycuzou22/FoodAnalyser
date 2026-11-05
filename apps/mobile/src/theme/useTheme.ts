import { DarkTheme, DefaultTheme, type Theme as NavigationTheme } from '@react-navigation/native';
import { useMemo } from 'react';
import { useColorScheme } from 'react-native';

import { palettes, radius, spacing, typography, type ColorPalette } from './tokens';

export interface AppTheme {
  scheme: 'light' | 'dark';
  colors: ColorPalette;
  spacing: typeof spacing;
  radius: typeof radius;
  typography: typeof typography;
  navigation: NavigationTheme;
}

export function buildTheme(scheme: 'light' | 'dark'): AppTheme {
  const colors = palettes[scheme];
  const base = scheme === 'dark' ? DarkTheme : DefaultTheme;
  return {
    scheme,
    colors,
    spacing,
    radius,
    typography,
    navigation: {
      ...base,
      colors: {
        ...base.colors,
        primary: colors.primary,
        background: colors.background,
        card: colors.surface,
        text: colors.text,
        border: colors.border,
      },
    },
  };
}

/** Thème qui suit le réglage clair / sombre du téléphone, sans redémarrage. */
export function useTheme(): AppTheme {
  const scheme = useColorScheme() === 'dark' ? 'dark' : 'light';
  return useMemo(() => buildTheme(scheme), [scheme]);
}
