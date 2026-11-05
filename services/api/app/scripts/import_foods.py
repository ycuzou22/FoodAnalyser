"""Importe une source de données nutritionnelles dans la table `foods`.

    python -m app.scripts.import_foods ciqual /data/ciqual_2025.xls --version 2025
    python -m app.scripts.import_foods off /data/en.openfoodfacts.org.products.csv.gz \\
        --version 2026-11-05

Les fichiers sources ne sont jamais commités (voir docs/sources-donnees.md).
"""

import argparse
import asyncio
import sys
from collections.abc import Iterator
from pathlib import Path

from app.core.config import get_settings
from app.core.logging import configure_logging
from app.db.session import create_engine, create_session_factory
from app.importers.ciqual import CiqualFormatError, read_ciqual
from app.importers.loader import ImportReport, SourceInfo, load_foods
from app.importers.off import read_off
from app.importers.records import FoodRecord
from app.models.enums import FoodSource

SOURCES = {
    "ciqual": {
        "source": FoodSource.CIQUAL,
        "license": "Licence Ouverte / Open Licence 2.0 (Etalab)",
        "attribution": "Anses. Table de composition nutritionnelle des aliments Ciqual.",
    },
    "off": {
        "source": FoodSource.OPEN_FOOD_FACTS,
        "license": "ODbL 1.0 (base) / DbCL 1.0 (contenus)",
        "attribution": "Open Food Facts contributors, https://world.openfoodfacts.org",
    },
}


def _limited(records: Iterator[FoodRecord], limit: int | None) -> Iterator[FoodRecord]:
    for count, record in enumerate(records, start=1):
        if limit is not None and count > limit:
            return
        yield record


async def run(kind: str, path: Path, version: str, limit: int | None) -> ImportReport:
    settings = get_settings()
    configure_logging(settings.log_level, json=settings.env != "development")
    # Ouvrir le fichier avant la base : un fichier invalide ne laisse aucune trace d'import.
    records = read_ciqual(path) if kind == "ciqual" else read_off(path)
    engine = create_engine(settings)
    info = SourceInfo(version=version, file_name=path.name, **SOURCES[kind])  # type: ignore[arg-type]
    try:
        async with create_session_factory(engine)() as session:
            return await load_foods(session, _limited(records, limit), info)
    finally:
        await engine.dispose()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("source", choices=sorted(SOURCES))
    parser.add_argument("path", type=Path)
    parser.add_argument("--version", required=True, help="version ou date de la source")
    parser.add_argument("--limit", type=int, help="nombre maximal de lignes lues (essais)")
    args = parser.parse_args(argv)

    if not args.path.is_file():
        print(f"✗ Fichier introuvable : {args.path}", file=sys.stderr)
        return 2
    try:
        report = asyncio.run(run(args.source, args.path, args.version, args.limit))
    except CiqualFormatError as exc:
        print(f"✗ {exc}", file=sys.stderr)
        return 1

    print(
        f"✔ {args.source} : {report.rows_read} lues, {report.rows_inserted} ajoutées, "
        f"{report.rows_updated} mises à jour, {report.rows_rejected} rejetées"
    )
    for reason, count in report.rejections.most_common():
        print(f"    {reason:<24} {count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
