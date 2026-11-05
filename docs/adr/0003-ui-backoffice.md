# ADR 0003 — Socle technique du back-office

- **Statut** : accepté
- **Date** : 2026-11-05
- **Issue** : #8

## Contexte

Le back-office sert à une poignée d'administrateurs : édition de la base d'aliments (#35), modération (#51), contenus (#48), tableau de bord (#52). Il est fait de tableaux, de formulaires et de fiches. Il doit être rapide à développer, accessible au clavier et ne jamais exposer de secret côté navigateur.

## Décisions

| Sujet | Choix | Alternatives écartées |
| --- | --- | --- |
| Outil de build | Vite 7 + plugin React **SWC** | Plugin React Babel : sa dépendance `semver@6` est bloquée par la politique `trustPolicy: no-downgrade` de pnpm ; SWC est aussi plus rapide |
| Interface | **Mantine 7** | shadcn/ui : composants à copier et maintenir soi-même, pas de tableau ni de formulaire complets prêts à l'emploi |
| Routage | React Router 7 (mode déclaratif) | TanStack Router : plus récent, équipe moins familière |
| Données serveur | TanStack Query 5 | Même outil que l'application mobile (#7) |
| Tests | Vitest 3 + Testing Library | Jest : configuration ESM plus lourde avec Vite |

## Sécurité

- **Pas de jeton en JavaScript** : l'administrateur est authentifié par un cookie de session `HttpOnly`, `Secure`, `SameSite=Strict` posé par l'API (#34). Le client envoie `credentials: 'include'` ; une faille XSS ne peut pas voler la session.
- **Le menu filtré par rôle n'est qu'un confort** : chaque appel est revérifié par l'API (`require_role`, #34).
- Toutes les routes sauf `/login` sont derrière `RequireAuth`, y compris la page 404, pour ne rien révéler de la structure.
- Pas de source maps en production ; `noindex, nofollow` dans le HTML.
- Les variables `VITE_*` sont intégrées au bundle : elles ne contiennent jamais de secret.

## Conséquences

- Les modules sont des pages provisoires jusqu'à leur issue.
- Le thème Mantine sera aligné sur les tokens du design system (#9).
