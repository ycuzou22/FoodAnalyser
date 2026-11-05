"""Chargement idempotent des aliments dans PostgreSQL (upsert par lots)."""

from collections import Counter
from collections.abc import Iterable
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any

import structlog
from sqlalchemy import Result, func, literal_column
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.importers.records import FoodRecord
from app.models import Food
from app.models.enums import FoodSource
from app.models.food_source import FoodSourceImport

BATCH_SIZE = 5_000

logger = structlog.get_logger("app.importers")


@dataclass(frozen=True)
class SourceInfo:
    source: FoodSource
    version: str
    license: str
    attribution: str
    file_name: str


@dataclass
class ImportReport:
    rows_read: int = 0
    rows_inserted: int = 0
    rows_updated: int = 0
    rejections: Counter[str] = field(default_factory=Counter)

    @property
    def rows_rejected(self) -> int:
        return sum(self.rejections.values())


# Colonne d'unicité utilisée pour l'upsert, selon la source.
_CONFLICT_KEY = {
    FoodSource.CIQUAL: "ciqual_code",
    FoodSource.OPEN_FOOD_FACTS: "barcode",
}

_UPDATED_COLUMNS = (
    "name",
    "brand",
    "kcal_100g",
    "protein_100g",
    "carbs_100g",
    "fat_100g",
    "fiber_100g",
    "salt_100g",
    "nutriscore",
    "popularity",
)


def _row(record: FoodRecord) -> dict[str, Any]:
    values = asdict(record)
    values["source"] = record.source
    return values


async def _flush(
    session: AsyncSession, source: FoodSource, rows: list[dict[str, Any]]
) -> tuple[int, int]:
    key = _CONFLICT_KEY[source]
    # Une même clé deux fois dans un lot ferait échouer « ON CONFLICT » : la dernière l'emporte.
    unique_rows = list({row[key]: row for row in rows}.values())

    base = insert(Food).values(unique_rows)
    upsert = base.on_conflict_do_update(
        index_elements=[key],
        set_={
            **{column: base.excluded[column] for column in _UPDATED_COLUMNS},
            "updated_at": func.now(),
        },
    )
    # xmax = 0 : la ligne vient d'être insérée ; sinon elle existait et a été mise à jour.
    result: Result[tuple[bool]] = await session.execute(
        upsert.returning(literal_column("(xmax = 0)").label("inserted"))
    )
    flags = [bool(inserted) for (inserted,) in result.all()]
    inserted = sum(flags)
    return inserted, len(flags) - inserted


async def load_foods(
    session: AsyncSession,
    records: Iterable[FoodRecord],
    info: SourceInfo,
    *,
    batch_size: int = BATCH_SIZE,
) -> ImportReport:
    """Valide et insère ou met à jour les aliments, puis trace l'import.

    Idempotent : relancer le même fichier met les lignes à jour sans créer de doublon.
    Chaque lot est validé (commit) séparément, pour qu'un import de plusieurs heures ne tienne
    pas une transaction ouverte.
    """
    report = ImportReport()
    trace = FoodSourceImport(
        source=info.source,
        source_version=info.version,
        license=info.license,
        attribution=info.attribution,
        file_name=info.file_name,
    )
    session.add(trace)
    await session.commit()

    batch: list[dict[str, Any]] = []
    for record in records:
        report.rows_read += 1
        reason = record.rejection_reason()
        if reason is not None:
            report.rejections[reason] += 1
            continue
        batch.append(_row(record))
        if len(batch) >= batch_size:
            inserted, updated = await _flush(session, info.source, batch)
            await session.commit()
            report.rows_inserted += inserted
            report.rows_updated += updated
            logger.info("food_import_progress", source=info.source, rows_read=report.rows_read)
            batch.clear()

    if batch:
        inserted, updated = await _flush(session, info.source, batch)
        report.rows_inserted += inserted
        report.rows_updated += updated

    trace.finished_at = datetime.now(UTC)
    trace.rows_read = report.rows_read
    trace.rows_inserted = report.rows_inserted
    trace.rows_updated = report.rows_updated
    trace.rows_rejected = report.rows_rejected
    trace.rejections = dict(report.rejections)
    await session.commit()
    return report
