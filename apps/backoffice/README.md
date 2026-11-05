# apps/backoffice

Back-office d'administration de FoodAnalyser (React 19, Vite 7, Mantine 7). Choix techniques : [ADR 0003](../../docs/adr/0003-ui-backoffice.md).

```bash
cp .env.example .env.local
pnpm --filter ./apps/backoffice dev     # http://localhost:5173
pnpm --filter ./apps/backoffice test
pnpm --filter ./apps/backoffice build
```

## Structure

```
src/
├── api/          client HTTP (cookie de session, erreurs problem+json → ApiError)
├── app/          routes, providers (Mantine, TanStack Query, auth), thème
├── components/   composants partagés
├── features/     un dossier par module : auth, foods, moderation, content, dashboard, users
├── layout/       AppShell et menu filtré par rôle
├── pages/        connexion, 404
└── test/         configuration et utilitaires de test
```

| Route | Module | Issue | Rôles |
| --- | --- | --- | --- |
| `/foods` | Aliments | #35 | admin, nutrition_editor |
| `/moderation` | Modération | #51 | admin, nutrition_editor |
| `/content` | Contenus | #48 | admin, content_editor |
| `/dashboard` | Tableau de bord | #52 | admin, analyst |
| `/users` | Utilisateurs | #34 | admin |
