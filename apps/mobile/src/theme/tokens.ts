/**
 * Jetons de design provisoires, remplacés par l'export du design system (issue #9).
 * Règle du cahier des charges : jamais de rouge pour signaler un dépassement calorique.
 */

export const spacing = { xs: 4, sm: 8, md: 16, lg: 24, xl: 32 } as const;

export const radius = { sm: 8, md: 12, lg: 20, full: 999 } as const;

export const typography = {
  title: { fontSize: 24, fontWeight: '700' },
  heading: { fontSize: 18, fontWeight: '600' },
  body: { fontSize: 16, fontWeight: '400' },
  caption: { fontSize: 13, fontWeight: '400' },
} as const;

export interface ColorPalette {
  background: string;
  surface: string;
  text: string;
  textMuted: string;
  primary: string;
  onPrimary: string;
  border: string;
  /** Information neutre (dépassement d'objectif, hors ligne) : jamais une couleur d'alerte. */
  notice: string;
  error: string;
}

// Contrastes texte / fond vérifiés ≥ 4,5:1 (WCAG AA, NFR-07).
export const palettes: Record<'light' | 'dark', ColorPalette> = {
  light: {
    background: '#F7F8F6',
    surface: '#FFFFFF',
    text: '#1B1F1C',
    textMuted: '#55605A',
    primary: '#1F7A5A',
    onPrimary: '#FFFFFF',
    border: '#DDE3DF',
    notice: '#8A5A00',
    error: '#B3261E',
  },
  dark: {
    background: '#111413',
    surface: '#1B1F1D',
    text: '#EEF2EF',
    textMuted: '#A9B3AD',
    primary: '#5FD3A6',
    onPrimary: '#06281C',
    border: '#2E3532',
    notice: '#F2C46D',
    error: '#F2B8B5',
  },
};
