from __future__ import annotations

import argparse
from pathlib import Path

from sqlalchemy import text

from app.config import ROOT_DIR
from app.db.base import Base
from app.db.seed import seed_database
from app.db.session import create_engine_and_session_factory
from app.models import contract, flower, purchase_order, supplier  # noqa: F401


SQL_DIR = ROOT_DIR / "app" / "sql"


def _execute_sql_file(engine, file_path: Path) -> None:
    content = file_path.read_text(encoding="utf-8")
    statements = [statement.strip() for statement in content.split(";") if statement.strip()]
    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))


def init_database(
    database_url: str | None = None,
    drop_existing: bool = False,
    with_seed: bool = False,
) -> None:
    engine, session_factory = create_engine_and_session_factory(database_url=database_url)

    if drop_existing:
        Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    _execute_sql_file(engine, SQL_DIR / "views.sql")
    _execute_sql_file(engine, SQL_DIR / "indexes.sql")

    if with_seed:
        seed_database(session_factory)


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize database schema and optional seed data.")
    parser.add_argument("--database-url", default=None, help="Alternative database URL.")
    parser.add_argument("--drop-existing", action="store_true", help="Drop all tables before creation.")
    parser.add_argument("--with-seed", action="store_true", help="Fill database with demo data.")
    args = parser.parse_args()
    init_database(
        database_url=args.database_url,
        drop_existing=args.drop_existing,
        with_seed=args.with_seed,
    )


if __name__ == "__main__":
    main()
