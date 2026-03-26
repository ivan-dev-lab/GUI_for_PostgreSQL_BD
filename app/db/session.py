from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings

_engine: Engine | None = None
_session_factory: sessionmaker[Session] | None = None


def _apply_sqlite_pragmas(engine: Engine) -> None:
    if engine.url.get_backend_name() != "sqlite":
        return

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, _connection_record) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def create_engine_and_session_factory(
    database_url: str | None = None,
    echo: bool = False,
) -> tuple[Engine, sessionmaker[Session]]:
    engine = create_engine(
        database_url or get_settings().database_url,
        echo=echo,
        future=True,
    )
    _apply_sqlite_pragmas(engine)
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False, future=True)
    return engine, factory


def get_engine() -> Engine:
    global _engine, _session_factory
    if _engine is None or _session_factory is None:
        _engine, _session_factory = create_engine_and_session_factory()
    return _engine


def get_session_factory() -> sessionmaker[Session]:
    global _engine, _session_factory
    if _engine is None or _session_factory is None:
        _engine, _session_factory = create_engine_and_session_factory()
    return _session_factory


@contextmanager
def session_scope(
    session_factory: sessionmaker[Session] | None = None,
) -> Iterator[Session]:
    factory = session_factory or get_session_factory()
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
