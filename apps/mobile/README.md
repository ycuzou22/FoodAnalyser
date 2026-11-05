# apps/mobile

Application iOS et Android de FoodAnalyser (Expo SDK 58, React Native 0.88, React 19). Choix techniques : [ADR 0002](../../docs/adr/0002-socle-mobile.md).

## Lancer l'application

Prérequis : Xcode (iOS, sur macOS) ou Android Studio avec un émulateur.

```bash
cp .env.example .env.local                 # URL de l'API
pnpm --filter ./apps/mobile ios            # ou : android
```

La première commande génère les projets natifs (`ios/`, `android/`, non versionnés) puis compile l'application.

## Vérifier

```bash
pnpm --filter ./apps/mobile lint
pnpm --filter ./apps/mobile typecheck
pnpm --filter ./apps/mobile test
```

## Structure

```
src/
├── api/          client HTTP (jeton, rafraîchissement unique, erreurs problem+json), TanStack Query
├── components/   bandeau hors ligne, gestion d'erreur
├── features/     un dossier par fonctionnalité (meal-analysis, journal…)
├── hooks/
├── i18n/         fr.json — tout texte visible passe par t('…'), vérifié par ESLint
├── navigation/   pile d'accueil + 5 onglets (Journal, Stats, Photo au centre, Recettes, Profil)
├── screens/
├── store/        session (Zustand), jetons dans le Keychain / Keystore
├── theme/        jetons de design, clair / sombre automatique
└── test/         doublures des modules natifs pour Jest
```

## Règles

- **Aucun texte en dur** dans le JSX : ESLint (`i18next/no-literal-string`) le refuse, y compris dans `accessibilityLabel` et `placeholder`.
- **Aucun jeton ni donnée de santé** dans `AsyncStorage` ou les logs.
- Un dépassement d'objectif n'est jamais affiché en rouge (couleur `notice`).
