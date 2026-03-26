from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

from app.constants import APP_TITLE, DEFAULT_USERS, DemoUser


ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")


@dataclass(frozen=True)
class AppSettings:
    app_title: str
    database_url: str
    init_with_seed: bool
    users: dict[str, DemoUser]


def _build_database_url() -> str:
    explicit_url = os.getenv("DATABASE_URL", "").strip()
    if explicit_url:
        return explicit_url

    driver = os.getenv("DB_DRIVER", "postgresql+psycopg")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    database = os.getenv("DB_NAME", "planting_material_accounting")
    username = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD", "postgres")
    return f"{driver}://{username}:{password}@{host}:{port}/{database}"


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    init_with_seed = os.getenv("APP_INIT_WITH_SEED", "true").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    return AppSettings(
        app_title=os.getenv("APP_TITLE", APP_TITLE),
        database_url=_build_database_url(),
        init_with_seed=init_with_seed,
        users=DEFAULT_USERS,
    )
