import { getLocales } from 'expo-localization';
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

import fr from './fr.json';

export const resources = { fr: { translation: fr } } as const;
export const SUPPORTED_LANGUAGES = Object.keys(resources);

/** Langue du téléphone si elle est disponible, sinon le français (NFR-08). */
export function detectLanguage(): string {
  const preferred = getLocales()[0]?.languageCode ?? 'fr';
  return SUPPORTED_LANGUAGES.includes(preferred) ? preferred : 'fr';
}

void i18n.use(initReactI18next).init({
  resources,
  lng: detectLanguage(),
  fallbackLng: 'fr',
  interpolation: { escapeValue: false }, // React échappe déjà
  returnNull: false,
});

export default i18n;
