// Étend la configuration partagée avec les règles React et l'interdiction des textes en dur.
import i18next from 'eslint-plugin-i18next';
import reactHooks from 'eslint-plugin-react-hooks';
import globals from 'globals';
import tseslint from 'typescript-eslint';

import shared from '../../eslint.config.js';

export default tseslint.config(
  ...shared,
  { ignores: ['.expo/**', 'android/**', 'ios/**', 'babel.config.js'] },
  {
    files: ['**/*.{ts,tsx}'],
    languageOptions: {
      globals: { ...globals.browser, __DEV__: 'readonly' },
    },
    plugins: { 'react-hooks': reactHooks },
    rules: {
      ...reactHooks.configs.recommended.rules,
    },
  },
  {
    // Tout texte visible passe par i18next (docs/conventions.md, NFR-08).
    files: ['src/**/*.tsx'],
    ignores: ['src/**/*.test.tsx', 'src/test/**'],
    ...i18next.configs['flat/recommended'],
    rules: {
      'i18next/no-literal-string': [
        'error',
        {
          mode: 'jsx-only',
          // Seuls les attributs vus ou entendus par l'utilisateur sont contrôlés ; les attributs
          // techniques (accessibilityRole, name d'un écran, testID…) restent libres.
          'jsx-attributes': {
            include: [
              'accessibilityLabel',
              'accessibilityHint',
              'placeholder',
              'title',
              'label',
              'tabBarAccessibilityLabel',
              'headerTitle',
            ],
          },
        },
      ],
    },
  },
);
