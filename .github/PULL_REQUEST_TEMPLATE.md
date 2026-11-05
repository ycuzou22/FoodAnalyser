<!-- Titre de la PR : [TAG] portée: description (#n°issue) -->

## Issue liée

Closes #

## Résumé

<!-- Ce que fait cette PR et pourquoi, en 2-3 phrases. -->

## Type de changement

- [ ] `[ADD]` nouvelle fonctionnalité
- [ ] `[UPDATE]` évolution d'une fonctionnalité
- [ ] `[FIX]` correction de bug
- [ ] `[REFACTO]` / `[STYLE]` sans changement fonctionnel
- [ ] `[SECU]` sécurité
- [ ] `[DOCS]` / `[CONFIG]` / `[TEST]` / `[DEPS]`
- [ ] Changement cassant (API, schéma de base, format de données)

## Portée

- [ ] mobile  - [ ] backoffice  - [ ] api  - [ ] ai  - [ ] db  - [ ] infra / ci

## Comment tester

1.
2.
3.

## Captures / démonstration

<!-- Obligatoire pour toute modification d'interface (avant / après). -->

## Checklist

- [ ] La branche suit la convention `type/n°-slug` et part de `develop`
- [ ] Les commits suivent la norme `[TAG] portée: description (#n°)`
- [ ] Tests ajoutés ou mis à jour, CI verte
- [ ] Migration de base réversible (si applicable)
- [ ] Documentation / OpenAPI à jour
- [ ] Aucun secret ni donnée personnelle réelle
- [ ] Contrôles d'accès vérifiés sur les nouveaux endpoints (pas d'IDOR)
- [ ] Nouveau flux de données, service tiers ou donnée personnelle : `docs/security/threat-model.md` mis à jour
- [ ] Textes de l'interface passés par l'i18n
