import os

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

DEFAULT_URL = "postgresql+psycopg2://postgres:postgres@localhost:5432/finanzas"

_engine: Engine | None = None


def get_engine() -> Engine:
    global _engine
    if _engine is None:
        _engine = create_engine(os.environ.get("FINZ_DB_URL", DEFAULT_URL))
    return _engine


def run_sql_file(path: str) -> None:
    with open(path, encoding="utf-8") as f:
        sql = f.read()
    with get_engine().begin() as conn:
        conn.execute(text(sql))
