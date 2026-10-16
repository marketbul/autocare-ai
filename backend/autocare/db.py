"""Thin DB-API wrapper so the same SQL runs on PostgreSQL (psycopg 3) and SQLite.

SQL is written with :name placeholders. For Postgres they are rewritten to
%(name)s. Rows come back as plain dicts.
"""
from __future__ import annotations

import re
import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

_NAMED = re.compile(r"(?<![:\w]):([A-Za-z_]\w*)")
SQL_DIR = Path(__file__).resolve().parent.parent / "sql"


class Database:
    def __init__(self, url: str):
        self.url = url
        self._lock = threading.Lock()
        if url.startswith("sqlite:///"):
            self.kind = "sqlite"
            path = url[len("sqlite:///"):] or ":memory:"
            # One shared connection: keeps ":memory:" databases alive and is
            # adequate for a single-process dev server.
            self._sqlite = sqlite3.connect(path, check_same_thread=False)
            self._sqlite.row_factory = sqlite3.Row
            self._sqlite.execute("PRAGMA foreign_keys = ON")
        elif url.startswith(("postgresql://", "postgres://")):
            self.kind = "postgres"
            import psycopg  # noqa: F401  (fail fast if missing)
        else:
            raise ValueError(f"Unsupported database URL: {url!r}")

    # -- connection handling -------------------------------------------------
    @contextmanager
    def _conn(self) -> Iterator[Any]:
        if self.kind == "sqlite":
            with self._lock:
                try:
                    yield self._sqlite
                    self._sqlite.commit()
                except Exception:
                    self._sqlite.rollback()
                    raise
        else:
            import psycopg
            from psycopg.rows import dict_row

            with psycopg.connect(self.url, row_factory=dict_row) as conn:
                yield conn  # psycopg commits on clean exit, rolls back on error

    def _sql(self, sql: str) -> str:
        return sql if self.kind == "sqlite" else _NAMED.sub(r"%(\1)s", sql)

    # -- public API ------------------------------------------------------------
    def query(self, sql: str, params: dict | None = None) -> list[dict]:
        with self._conn() as conn:
            cur = conn.execute(self._sql(sql), params or {})
            return [dict(r) for r in cur.fetchall()]

    def execute(self, sql: str, params: dict | None = None) -> None:
        with self._conn() as conn:
            conn.execute(self._sql(sql), params or {})

    def executemany(self, sql: str, rows: list[dict]) -> None:
        if not rows:
            return
        with self._conn() as conn:
            if self.kind == "sqlite":
                conn.executemany(sql, rows)
            else:
                with conn.cursor() as cur:
                    cur.executemany(self._sql(sql), rows)

    def create_schema(self) -> None:
        name = "schema.sqlite.sql" if self.kind == "sqlite" else "schema.postgres.sql"
        script = (SQL_DIR / name).read_text(encoding="utf-8")
        with self._conn() as conn:
            if self.kind == "sqlite":
                conn.executescript(script)
            else:
                conn.execute(script)

    def vector_param(self, name: str) -> str:
        """SQL expression for an embedding parameter (pgvector needs a cast)."""
        return f"CAST(:{name} AS vector)" if self.kind == "postgres" else f":{name}"
