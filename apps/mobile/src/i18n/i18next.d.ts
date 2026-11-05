import 'i18next';

import type fr from './fr.json';

// Clés de traduction vérifiées par TypeScript : t('tabs.journl') ne compile pas.
declare module 'i18next' {
  interface CustomTypeOptions {
    defaultNS: 'translation';
    resources: { translation: typeof fr };
  }
}
