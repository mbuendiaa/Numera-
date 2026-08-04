"""Comprueba la conexión y muestra el número de registros por tabla."""

from __future__ import annotations

import sys
from pathlib import Path

from sqlalchemy import func, select, text

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from numera.core.config import settings  # noqa: E402
from numera.infrastructure.database.base import Base  # noqa: E402
from numera.infrastructure.database.session import engine  # noqa: E402
from numera.infrastructure.persistence import models  # noqa: F401,E402

with engine.connect() as connection:
    connection.execute(text("SELECT 1"))
    print("Conexión correcta")
    print("Motor:", engine.dialect.name)
    for table in Base.metadata.sorted_tables:
        count = connection.execute(select(func.count()).select_from(table)).scalar_one()
        print(f"{table.name}: {count}")
