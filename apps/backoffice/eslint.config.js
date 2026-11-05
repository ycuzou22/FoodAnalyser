// Étend la configuration partagée du monorepo avec les règles React.
import reactHooks from 'eslint-plugin-react-hooks';
import reactRefresh from 'eslint-plugin-react-refresh';
import globals from 'globals';
import tseslint from 'typescript-eslint';

import shared from '../../eslint.config.js';

export default tseslint.config(...shared, {
  files: ['**/*.{ts,tsx}'],
  languageOptions: {
    globals: { ...globals.browser },
  },
  plugins: {
    'react-hooks': reactHooks,
    'react-refresh': reactRefresh,
  },
  rules: {
    ...reactHooks.configs.recommended.rules,
    'react-refresh/only-export-components': ['warn', { allowConstantExport: true }],
  },
});
