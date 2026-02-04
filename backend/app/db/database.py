"""SQLite connection and lifecycle."""
import sqlite3
from contextlib import contextmanager
from pathlib import Path

from backend.app.core.config import DATABASE_PATH, DATA_DIR
from backend.app.db.models import create_tables_sql


def get_sqlite_path() -> Path:
    """Return absolute path to SQLite database file."""
    p = DATABASE_PATH
    if str(p).startswith("sqlite:///"):
        p = Path(str(p).replace("sqlite:///", ""))
    if not p.is_absolute():
        p = Path.cwd() / p
    return p


@contextmanager
def get_connection():
    """Yield a database connection; creates DB file and dir if needed."""
    path = get_sqlite_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    # Enforce FK constraints in SQLite for each connection.
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    """Create tables if they do not exist."""
    path = get_sqlite_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with get_connection() as conn:
        conn.executescript(create_tables_sql())
