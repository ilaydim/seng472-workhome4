# src/db.py
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "db" / "northwind.sqlite"

def get_conn():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def run_sql(sql: str, params: tuple = ()):
    with get_conn() as conn:
        cur = conn.execute(sql, params)
        # SELECT mi değil mi basit kontrol:
        if sql.strip().lower().startswith("select"):
            rows = [dict(row) for row in cur.fetchall()]
            cols = [d[0] for d in cur.description] if cur.description else []
            return {"columns": cols, "rows": rows}
        else:
            conn.commit()
            return {"columns": [], "rows": [], "affected": cur.rowcount}
