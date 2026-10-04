"""Tiny SQLite store: every engine run is saved so the demo can show history."""
import json
import sqlite3
from datetime import datetime, timezone

from .config import DB_PATH


def _conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with _conn() as c:
        c.execute(
            """CREATE TABLE IF NOT EXISTS runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                engine TEXT NOT NULL,
                input_json TEXT NOT NULL,
                result_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            )"""
        )


def save_run(engine, data, result):
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with _conn() as c:
        cur = c.execute(
            "INSERT INTO runs (engine, input_json, result_json, created_at) VALUES (?, ?, ?, ?)",
            (engine, json.dumps(data), json.dumps(result), now),
        )
        return cur.lastrowid


def list_runs(limit=20):
    with _conn() as c:
        rows = c.execute(
            "SELECT id, engine, created_at, result_json FROM runs ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    out = []
    for r in rows:
        summary = json.loads(r["result_json"]).get("summary", {})
        out.append(
            {"id": r["id"], "engine": r["engine"], "created_at": r["created_at"], "summary": summary}
        )
    return out


def get_run(run_id):
    with _conn() as c:
        r = c.execute("SELECT * FROM runs WHERE id = ?", (run_id,)).fetchone()
    if r is None:
        return None
    return {
        "id": r["id"],
        "engine": r["engine"],
        "created_at": r["created_at"],
        "input": json.loads(r["input_json"]),
        "result": json.loads(r["result_json"]),
    }
