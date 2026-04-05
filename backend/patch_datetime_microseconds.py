"""
Patch script: strip microseconds from all datetime columns in portfolio.db.

Affected columns:
  - positions.closing_date
  - trades.date
  - transactions.date
  - ohlcvs.timestamp

Run from the backend/ directory:
    python patch_datetime_microseconds.py
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "portfolio.db"

COLUMNS = [
    ("positions",    "closing_date"),
    ("trades",       "date"),
    ("transactions", "date"),
    ("ohlcvs",       "timestamp"),
]


def strip_microseconds(value: str) -> str:
    """'2024-06-03 14:06:00.000000' -> '2024-06-03 14:06:00'"""
    if value and "." in value:
        return value.split(".")[0]
    return value


def patch(conn: sqlite3.Connection, table: str, column: str) -> int:
    cur = conn.execute(f"SELECT id, {column} FROM {table} WHERE {column} LIKE '%.%'")
    rows = cur.fetchall()
    updated = 0
    for row_id, raw_value in rows:
        patched = strip_microseconds(raw_value)
        conn.execute(
            f"UPDATE {table} SET {column} = ? WHERE id = ?",
            (patched, row_id),
        )
        updated += 1
    return updated


def main():
    if not DB_PATH.exists():
        print(f"Database not found: {DB_PATH}")
        return

    print(f"Patching {DB_PATH}\n")
    with sqlite3.connect(DB_PATH) as conn:
        for table, column in COLUMNS:
            count = patch(conn, table, column)
            print(f"  {table}.{column}: {count} row(s) updated")
        conn.commit()
    print("\nDone.")


if __name__ == "__main__":
    main()
