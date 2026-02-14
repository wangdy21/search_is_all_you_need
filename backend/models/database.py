import sqlite3
import threading
from contextlib import contextmanager

from backend.config import get_config
from backend.models.schemas import SCHEMA_SQL

_local = threading.local()


def _get_raw_connection():
    """Get a thread-local SQLite connection."""
    if not hasattr(_local, "connection") or _local.connection is None:
        config = get_config()
        conn = sqlite3.connect(str(config.DATABASE_PATH), timeout=10)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=5000")
        conn.execute("PRAGMA foreign_keys=ON")
        _local.connection = conn
    return _local.connection


@contextmanager
def get_connection():
    """Context manager for database connections with auto-commit."""
    conn = _get_raw_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise


def init_db():
    """Initialize database: create tables if they don't exist."""
    config = get_config()
    config.DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(config.DATABASE_PATH))
    conn.executescript(SCHEMA_SQL)
    conn.close()


def close_connection():
    """Close thread-local connection."""
    if hasattr(_local, "connection") and _local.connection is not None:
        _local.connection.close()
        _local.connection = None
