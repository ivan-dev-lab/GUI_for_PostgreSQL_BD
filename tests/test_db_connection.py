from __future__ import annotations

from sqlalchemy import text

from app.db.base import Base
from app.db.session import create_engine_and_session_factory
from app.models import Contract, Flower, PurchaseOrder, Supplier  # noqa: F401


def test_db_connection_and_schema_creation(tmp_path):
    database_path = tmp_path / "connection.sqlite"
    engine, _factory = create_engine_and_session_factory(f"sqlite:///{database_path}")
    Base.metadata.create_all(bind=engine)

    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1")).scalar_one()

    assert result == 1
    engine.dispose()
