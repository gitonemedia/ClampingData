#!/usr/bin/env python3
"""
Add missing clamp fields to an existing SQLite DB.

Usage:
    python scripts/add_clamp_fields.py [path/to/db]

If no path is provided the script will try `instance/clamping_business.db` and
`clamping_business.db` in the repo root.
"""
import sqlite3
import os
import sys

DEFAULT_CANDIDATES = [
    os.path.join('instance', 'clamping_business.db'),
    os.path.abspath('clamping_business.db')
]

NEW_COLUMNS = [
    ('clamp_data', 'image_path', 'TEXT', "''"),
    ('clamp_data', 'time_called', 'TEXT', "''"),
    ('clamp_data', 'car_type', 'TEXT', "''"),
    ('clamp_data', 'color', 'TEXT', "''"),
    ('clamp_data', 'clamp_reference', 'TEXT', "''"),
]


def column_exists(conn, table, column):
    cur = conn.execute(f"PRAGMA table_info('{table}')")
    cols = [r[1] for r in cur.fetchall()]
    return column in cols


def add_column(conn, table, col, coltype, default):
    if column_exists(conn, table, col):
        print(f"Column {col} already exists on {table}")
        return False
    sql = f"ALTER TABLE {table} ADD COLUMN {col} {coltype} DEFAULT {default}"
    conn.execute(sql)
    print(f"Added column {col} to {table}")
    return True


def main():
    db_path = None
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
        if not os.path.exists(db_path):
            print(f"Database not found at {db_path}")
            return
    else:
        for cand in DEFAULT_CANDIDATES:
            if os.path.exists(cand):
                db_path = cand
                break
    if not db_path:
        print('No database file found. Provide path as the first argument.')
        return

    conn = sqlite3.connect(db_path)
    try:
        migrated = False
        for table, col, coltype, default in NEW_COLUMNS:
            try:
                changed = add_column(conn, table, col, coltype, default)
                if changed:
                    migrated = True
            except sqlite3.OperationalError as e:
                print(f"Skipping {table}.{col}: {e}")
        if migrated:
            conn.commit()
            print('Migration complete.')
        else:
            print('No changes needed.')
    finally:
        conn.close()


if __name__ == '__main__':
    main()
