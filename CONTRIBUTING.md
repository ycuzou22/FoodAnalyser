# Contribuer à FoodAnalyser

Toutes les règles détaillées sont dans [docs/conventions.md](docs/conventions.md). L'essentiel :

1. **Prendre une issue** : s'assigner, passer la carte en *In progress* dans le GitHub Project.
2. **Créer la branche** depuis `develop` :
   ```bash
   git switch develop && git pull
   git switch -c feature/12-photo-meal-analysis
   ```
3. **Commiter** au format `[TAG] portée: description (#12)` :
   ```bash
   git commit -m "[ADD] api: endpoint POST /meals/analyze (#12)"
   ```
   Tags : `[ADD]` `[UPDATE]` `[FIX]` `[DEL]` `[REFACTO]` `[STYLE]` `[DOCS]` `[TEST]` `[CONFIG]` `[DEPS]` `[PERF]` `[SECU]` `[MERGE]` `[RELEASE]`.
4. **Ouvrir une PR** vers `develop` avec le modèle fourni et `Closes #12`.
5. **Revue** : 1 approbation + CI verte, puis *Squash and merge*. La branche est supprimée.

## Définition de « terminé » (Definition of Done)

- [ ] Critères d'acceptation de l'issue vérifiés
- [ ] Tests écrits et verts, couverture non dégradée
- [ ] Lint, typage et analyse de sécurité verts
- [ ] Documentation mise à jour (README, OpenAPI, ADR si décision)
- [ ] Aucun secret, aucune donnée personnelle réelle dans le code ou les fixtures
- [ ] PR relue et approuvée

## Intégration continue

| Workflow | Déclenché par | Vérifie |
| --- | --- | --- |
| `repo-ci` | toutes les PR | Prettier, ESLint, vérificateur de commits, Compose, scripts shell |
| `pr-title` | toutes les PR | Titre au format `[TAG] portée: description (#n°)` |
| `security` | toutes les PR + chaque lundi | gitleaks (historique complet), Semgrep (OWASP Top 10), Trivy (CVE et Dockerfile) |
| `api-ci` | `services/api/**` | Ruff, mypy strict, pytest + intégration PostgreSQL 16, couverture ≥ 70 % commentée sur la PR |
| `ai-ci` | `services/ai/**` | Ruff, mypy, pytest |
| `mobile-ci` / `backoffice-ci` | `apps/…/**` | ESLint, TypeScript, tests (et build pour le back-office) |

Dependabot propose chaque lundi les mises à jour regroupées (uv, npm, Docker, Actions) vers `develop`.

La protection de `main` et `develop` se configure une fois avec `bash infra/scripts/protect-branches.sh`.
