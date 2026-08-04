"""Migra todos los datos de Numera desde SQLite a PostgreSQL.

Uso desde la carpeta backend:
    python scripts/migrate_sqlite_to_postgresql.py \
        --sqlite ./numera.db \
        --postgresql postgresql+psycopg://numera:numera@localhost:5432/numera

La base PostgreSQL de destino debe estar vacía. Use --replace para vaciar las
 tablas de Numera del destino antes de copiar.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from sqlalchemy import create_engine, func, inspect, select

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from numera.infrastructure.database.base import Base  # noqa: E402
from numera.infrastructure.persistence import models  # noqa: F401,E402


def sqlite_url(path: str) -> str:
    db_path = Path(path).expanduser().resolve()
    if not db_path.exists():
        raise FileNotFoundError(f"No existe la base SQLite: {db_path}")
    return f"sqlite:///{db_path.as_posix()}"


def table_count(connection, table) -> int:
    return int(connection.execute(select(func.count()).select_from(table)).scalar_one())


def main() -> int:
    parser = argparse.ArgumentParser(description="Migra Numera de SQLite a PostgreSQL")
    parser.add_argument("--sqlite", default="./numera.db", help="Ruta al archivo numera.db")
    parser.add_argument("--postgresql", required=True, help="URL postgresql+psycopg://...")
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Vacía las tablas Numera del destino antes de copiar",
    )
    parser.add_argument("--batch-size", type=int, default=500)
    args = parser.parse_args()

    if not args.postgresql.startswith(("postgresql://", "postgresql+psycopg://")):
        parser.error("--postgresql debe ser una URL de PostgreSQL")

    source = create_engine(sqlite_url(args.sqlite))
    target = create_engine(args.postgresql, pool_pre_ping=True)

    source_tables = set(inspect(source).get_table_names())
    expected_tables = {table.name for table in Base.metadata.sorted_tables}
    missing = expected_tables - source_tables
    if missing:
        print("Aviso: no existen en SQLite y se omitirán:", ", ".join(sorted(missing)))

    Base.metadata.create_all(target)

    with target.begin() as target_conn:
        populated = {
            table.name: table_count(target_conn, table)
            for table in Base.metadata.sorted_tables
            if table.name in source_tables
        }
        nonempty = {name: count for name, count in populated.items() if count}
        if nonempty and not args.replace:
            details = ", ".join(f"{name}={count}" for name, count in nonempty.items())
            raise RuntimeError(
                "La base PostgreSQL no está vacía. Use --replace para reemplazarla. " + details
            )
        if args.replace:
            for table in reversed(Base.metadata.sorted_tables):
                target_conn.execute(table.delete())

    copied: dict[str, int] = {}
    with source.connect() as source_conn, target.begin() as target_conn:
        for table in Base.metadata.sorted_tables:
            if table.name not in source_tables:
                continue
            rows = source_conn.execute(select(table)).mappings()
            batch = []
            total = 0
            for row in rows:
                batch.append(dict(row))
                if len(batch) >= args.batch_size:
                    target_conn.execute(table.insert(), batch)
                    total += len(batch)
                    batch.clear()
            if batch:
                target_conn.execute(table.insert(), batch)
                total += len(batch)
            copied[table.name] = total
            print(f"{table.name}: {total} registros")

    errors = []
    with source.connect() as source_conn, target.connect() as target_conn:
        for table in Base.metadata.sorted_tables:
            if table.name not in source_tables:
                continue
            source_count = table_count(source_conn, table)
            target_count = table_count(target_conn, table)
            if source_count != target_count:
                errors.append(f"{table.name}: SQLite={source_count}, PostgreSQL={target_count}")

    if errors:
        print("Migración terminada con diferencias:")
        for error in errors:
            print(" -", error)
        return 1

    print(f"Migración completada: {sum(copied.values())} registros copiados.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
