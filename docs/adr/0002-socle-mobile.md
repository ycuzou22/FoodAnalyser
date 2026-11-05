# ADR 0002 — Socle de l'application mobile

- **Statut** : accepté
- **Date** : 2026-11-05
- **Issue** : #7

## Contexte

L'application iOS et Android est le produit principal. Elle a besoin de la caméra avec profondeur (#24), d'un stockage sécurisé (#16, #76), des achats intégrés (#32), de la synchronisation santé (#49) et de mises à jour fréquentes. L'équipe compte deux développeurs mobiles.

## Décision : Expo (SDK 58) avec génération des projets natifs

| Option | Pour | Contre |
| --- | --- | --- |
| **Expo SDK 58 + prebuild** (retenu) | Recommandé par l'équipe React Native ; versions natives cohérentes entre elles (`bundledNativeModules.json`) ; dossiers `ios/` et `android/` générés, pas maintenus à la main ; builds cloud EAS possibles | Modules natifs sur mesure via des *config plugins* |
| React Native CLI | Contrôle total des projets natifs | Mises à jour de React Native manuelles et coûteuses, dossiers natifs à maintenir |
| Flutter | Bonnes performances | Pas de partage de code ni de compétences avec le back-office React |

Les dossiers `ios/` et `android/` ne sont **pas commités** : ils sont générés par `expo prebuild` à partir de `app.json`. Toute configuration native passe par `app.json` ou un plugin.

## Bibliothèques

| Besoin | Choix | Remarque |
| --- | --- | --- |
| Navigation | React Navigation 7 (pile + onglets) | Demandé par l'issue ; Expo Router écarté pour garder la navigation explicite |
| Données serveur | TanStack Query 5 | Branché sur NetInfo (en ligne / hors ligne) et AppState (premier plan) |
| État local | Zustand 5 | Session uniquement pour l'instant |
| Jetons | **expo-secure-store** | Keychain / Keystore, `WHEN_UNLOCKED_THIS_DEVICE_ONLY`. Remplace `react-native-keychain` cité dans l'issue : même garantie, module maintenu par Expo |
| Traductions | i18next + react-i18next | Clés typées : une clé inexistante ne compile pas |
| Tests | Jest 30 + jest-expo + Testing Library 14 | Testing Library 14 : `render`, `fireEvent`, `act` sont asynchrones |

## Sécurité

- Les jetons ne sont jamais dans `AsyncStorage` (fichier en clair).
- Le refresh token est rotatif : le client garantit **un seul** rafraîchissement à la fois, même si plusieurs requêtes reçoivent un 401 en même temps (deux rafraîchissements parallèles déclencheraient la détection de réutilisation et révoqueraient la session).
- Android : `allowBackup: false`, et les clés du stockage sécurisé sont exclues des sauvegardes.
- `EXPO_PUBLIC_*` est intégré à l'application : jamais de secret.
- Le reste de la protection des données sur l'appareil (cache chiffré, écran masqué, notifications neutres) est traité par #76.

## Chaîne d'approvisionnement

Babel (indispensable à React Native) dépend de `semver@6.3.1`, bloqué par la règle pnpm `trustPolicy: no-downgrade`. Cette **seule version** est exemptée dans `pnpm-workspace.yaml`, avec sa justification, après validation du responsable du dépôt le 5 novembre 2026.

## Conséquences

- Lancer l'app demande un *development build* (`pnpm --filter ./apps/mobile ios` / `android`), pas Expo Go, dès qu'un module natif hors SDK est ajouté (caméra, achats).
- Les versions des modules natifs suivent le SDK : on met à jour Expo et ses modules ensemble.
