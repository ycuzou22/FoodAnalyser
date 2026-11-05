#!/usr/bin/env bash
# Protège main et develop : PR obligatoire, vérifications CI requises, pas de force-push.
#
# À lancer UNE FOIS, après la fusion des workflows CI dans develop (les vérifications
# doivent avoir tourné au moins une fois pour que GitHub les connaisse) :
#   bash infra/scripts/protect-branches.sh            # projet solo : 0 approbation requise
#   APPROVALS=1 bash infra/scripts/protect-branches.sh  # dès qu'il y a un second développeur
#
# Seules les vérifications qui tournent sur TOUTES les PR sont exigées. Les workflows filtrés
# par dossier (api-ci, ai-ci, mobile-ci, backoffice-ci) ne sont pas lancés sur une PR qui ne
# touche pas leur dossier : les exiger bloquerait ces PR indéfiniment. Ils restent bloquants
# en pratique, puisqu'une PR avec un job en échec ne doit pas être fusionnée.

set -euo pipefail

REPO="ycuzou22/FoodAnalyser"
APPROVALS="${APPROVALS:-0}"

REQUIRED_CHECKS='[
  {"context": "format, lint racine et scripts"},
  {"context": "secrets (gitleaks)"},
  {"context": "SAST (Semgrep)"},
  {"context": "dépendances et configuration (Trivy)"},
  {"context": "format du titre"}
]'

for branch in main develop; do
  echo "→ Protection de $branch"
  gh api -X PUT "repos/$REPO/branches/$branch/protection" --input - >/dev/null <<EOF
{
  "required_status_checks": { "strict": true, "checks": $REQUIRED_CHECKS },
  "enforce_admins": false,
  "required_pull_request_reviews": {
    "required_approving_review_count": $APPROVALS,
    "dismiss_stale_reviews": true
  },
  "restrictions": null,
  "required_linear_history": false,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "required_conversation_resolution": true
}
EOF
done

echo "✔ main et develop protégées ($APPROVALS approbation(s) requise(s))."
