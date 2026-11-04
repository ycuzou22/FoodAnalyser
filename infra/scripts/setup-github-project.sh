#!/usr/bin/env bash
# Crée le GitHub Project « FoodAnalyser » et y range toutes les issues du dépôt.
#
# Prérequis : GitHub CLI (gh) connecté avec le scope « project » :
#   gh auth login
#   gh auth refresh -s project
# Lancement (Linux, macOS, ou Git Bash sous Windows) :
#   bash infra/scripts/setup-github-project.sh
#
# Le script est idempotent pour l'ajout d'issues (une issue déjà présente est mise à jour),
# mais crée un nouveau Project à chaque lancement : ne le lancer qu'une fois.

set -euo pipefail

OWNER="ycuzou22"
REPO="FoodAnalyser"
TITLE="FoodAnalyser"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

echo "→ Vérification de l'authentification gh"
gh auth status >/dev/null

echo "→ Création du Project « $TITLE »"
NUM=$(gh project create --owner "$OWNER" --title "$TITLE" --format json --jq '.number')
PID=$(gh project view "$NUM" --owner "$OWNER" --format json --jq '.id')
gh project link "$NUM" --owner "$OWNER" --repo "$OWNER/$REPO" >/dev/null
gh project edit "$NUM" --owner "$OWNER" \
  --description "Suivi du développement de FoodAnalyser (application de nutrition par photo)" \
  --readme "Colonnes : Backlog → Ready → In progress → In review → Done. Conventions : docs/conventions.md" >/dev/null

echo "→ Configuration du champ Status"
STATUS_ID=$(gh project field-list "$NUM" --owner "$OWNER" --format json --jq '.fields[] | select(.name=="Status") | .id')
gh api graphql -f fieldId="$STATUS_ID" -f query='
mutation($fieldId: ID!) {
  updateProjectV2Field(input: {
    fieldId: $fieldId
    singleSelectOptions: [
      {name: "Backlog",     color: GRAY,   description: "Pas encore prête : dépendances ouvertes ou besoin de précision"}
      {name: "Ready",       color: BLUE,   description: "Prête à être prise"}
      {name: "In progress", color: YELLOW, description: "En cours, branche créée"}
      {name: "In review",   color: PURPLE, description: "PR ouverte, en revue"}
      {name: "Done",        color: GREEN,  description: "Fusionnée et vérifiée"}
    ]
  }) { projectV2Field { ... on ProjectV2SingleSelectField { id } } }
}' >/dev/null

echo "→ Création des champs personnalisés"
gh project field-create "$NUM" --owner "$OWNER" --name "Priorité" --data-type SINGLE_SELECT \
  --single-select-options "Must,Should,Could" >/dev/null
gh project field-create "$NUM" --owner "$OWNER" --name "Taille" --data-type SINGLE_SELECT \
  --single-select-options "XS,S,M,L,XL" >/dev/null
gh project field-create "$NUM" --owner "$OWNER" --name "Phase" --data-type SINGLE_SELECT \
  --single-select-options "M1 - Cadrage et design,M2 - MVP,M3 - Bêta fermée,M4 - Lancement V1,Backlog V2" >/dev/null
gh project field-create "$NUM" --owner "$OWNER" --name "Début" --data-type DATE >/dev/null
gh project field-create "$NUM" --owner "$OWNER" --name "Échéance" --data-type DATE >/dev/null
gh project field-create "$NUM" --owner "$OWNER" --name "Estimation (j)" --data-type NUMBER >/dev/null

# Cache des identifiants : "champ<TAB>option<TAB>id_option<TAB>id_champ"
gh project field-list "$NUM" --owner "$OWNER" --format json \
  --jq '.fields[] | select(.options != null) | .id as $f | .name as $n | .options[] | "\($n)\t\(.name)\t\(.id)\t\($f)"' \
  > "$TMP/options.tsv"

field_id() { awk -F'\t' -v f="$1" '$1==f {print $4; exit}' "$TMP/options.tsv"; }
option_id() { awk -F'\t' -v f="$1" -v o="$2" '$1==f && $2==o {print $3; exit}' "$TMP/options.tsv"; }
set_select() { # item champ option
  local fid oid
  fid=$(field_id "$2"); oid=$(option_id "$2" "$3")
  [ -n "$oid" ] && gh project item-edit --id "$1" --project-id "$PID" --field-id "$fid" --single-select-option-id "$oid" >/dev/null
}
EST_ID=$(gh project field-list "$NUM" --owner "$OWNER" --format json --jq '.fields[] | select(.name=="Estimation (j)") | .id')

echo "→ Ajout des issues"
gh api --paginate "repos/$OWNER/$REPO/issues?state=all&per_page=100" \
  --jq '.[] | select(.pull_request | not) | [.number, .html_url, (.milestone.title // ""), ([.labels[].name] | join(","))] | @tsv' \
  > "$TMP/issues.tsv"

COUNT=0
while IFS=$'\t' read -r number url milestone labels; do
  item=$(gh project item-add "$NUM" --owner "$OWNER" --url "$url" --format json --jq '.id')

  case ",$labels," in *",priority: must,"*) set_select "$item" "Priorité" "Must";;
                      *",priority: should,"*) set_select "$item" "Priorité" "Should";;
                      *",priority: could,"*) set_select "$item" "Priorité" "Could";; esac

  for s in XS S M L XL; do
    case ",$labels," in *",size: $s,"*)
      set_select "$item" "Taille" "$s"
      case $s in XS) est=0.25;; S) est=0.5;; M) est=1.5;; L) est=4;; XL) est=8;; esac
      gh project item-edit --id "$item" --project-id "$PID" --field-id "$EST_ID" --number "$est" >/dev/null;;
    esac
  done

  [ -n "$milestone" ] && set_select "$item" "Phase" "$milestone"

  case ",$labels," in *",status: ready,"*) set_select "$item" "Status" "Ready";;
                      *) set_select "$item" "Status" "Backlog";; esac

  COUNT=$((COUNT + 1))
  printf '  #%s ajoutée\n' "$number"
done < "$TMP/issues.tsv"

URL=$(gh project view "$NUM" --owner "$OWNER" --format json --jq '.url')
echo
echo "✔ Project créé avec $COUNT issues : $URL"
echo
echo "Dernières étapes dans l'interface (non disponibles via l'API) :"
echo "  1. Vue « Tableau » : Layout Board, Group by Status"
echo "  2. Vue « Roadmap » : Layout Roadmap, dates Début / Échéance, Group by Phase"
echo "  3. Vue « Par phase » : Layout Table, Group by Phase, tri par Priorité"
echo "  4. Workflows : activer « Auto-add to project » (filtre repo:$OWNER/$REPO is:issue),"
echo "     « Item closed → Done », « Pull request merged → Done », « Pull request opened → In review »"
