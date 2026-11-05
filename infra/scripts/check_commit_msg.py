#!/usr/bin/env python3
"""Vérifie qu'un message de commit (ou un titre de PR) respecte docs/conventions.md §2.

Format : [TAG] portée: description (#n°issue)

Utilisation :
    python3 infra/scripts/check_commit_msg.py .git/COMMIT_EDITMSG   # hook commit-msg
    python3 infra/scripts/check_commit_msg.py --text "[ADD] api: ..."  # titre de PR en CI
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

TAGS = (
    "ADD",
    "UPDATE",
    "FIX",
    "DEL",
    "REFACTO",
    "STYLE",
    "DOCS",
    "TEST",
    "CONFIG",
    "DEPS",
    "PERF",
    "SECU",
    "MERGE",
    "RELEASE",
)
SCOPES = ("mobile", "backoffice", "api", "ai", "db", "infra", "ci", "docs", "repo")
SCOPE_OPTIONAL = ("MERGE", "RELEASE")  # « [MERGE] develop dans main pour v0.2.0 »
MAX_LENGTH = 72

PATTERN = re.compile(
    rf"^\[(?P<tag>{'|'.join(TAGS)})\] "
    rf"(?:(?P<scope>{'|'.join(SCOPES)}): )?"
    r"(?P<description>\S.*?)"
    r"(?P<issue> \(#\d+\))?$"
)

# Messages générés automatiquement par Git ou par les outils de revue : on les laisse passer.
AUTO_GENERATED = re.compile(r"^(Merge |Revert \"|fixup! |squash! |amend! )")


def first_line(message: str) -> str:
    """Première ligne non vide et non commentée du message."""
    for line in message.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            return stripped
    return ""


def check(message: str) -> list[str]:
    """Renvoie la liste des erreurs (vide si le message est conforme)."""
    subject = first_line(message)
    if not subject:
        return ["Le message de commit est vide."]
    if AUTO_GENERATED.match(subject):
        return []

    match = PATTERN.match(subject)
    if match is None:
        return [
            f"Format invalide : « {subject} »",
            "Attendu : [TAG] portée: description (#n°issue)",
            f"  TAG    : {', '.join(TAGS)}",
            f"  portée : {', '.join(SCOPES)}",
            "  Exemple : [ADD] api: endpoint POST /meals/analyze (#23)",
        ]

    errors: list[str] = []
    if match["scope"] is None and match["tag"] not in SCOPE_OPTIONAL:
        errors.append(f"Portée manquante après [{match['tag']}] : {', '.join(SCOPES)}.")
    if match["tag"] != "MERGE" and match["issue"] is None:
        errors.append("La référence d'issue « (#n°) » est obligatoire en fin de ligne (sauf [MERGE]).")
    if len(subject) > MAX_LENGTH:
        errors.append(f"Première ligne trop longue : {len(subject)} caractères (max {MAX_LENGTH}).")
    if match["description"].rstrip().endswith("."):
        errors.append("Pas de point final dans la description.")
    return errors


def main(argv: list[str]) -> int:
    if len(argv) == 3 and argv[1] == "--text":
        message = argv[2]
    elif len(argv) == 2:
        message = Path(argv[1]).read_text(encoding="utf-8")
    else:
        print(__doc__, file=sys.stderr)
        return 2

    errors = check(message)
    for error in errors:
        print(f"✗ {error}", file=sys.stderr)
    if errors:
        print("Voir docs/conventions.md §2.", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
