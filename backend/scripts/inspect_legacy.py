#!/usr/bin/env python3
"""Inspect legacy database schema"""
import sqlite3
from pathlib import Path

BACKUP_DIR = Path(__file__).parent.parent.parent / "backups" / "backup_20260222_155523"
SOURCE_DB = BACKUP_DIR / "safeplan.db"

print(f"[*] Database: {SOURCE_DB}")

conn = sqlite3.connect(str(SOURCE_DB))
cur = conn.cursor()

# Get tables
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cur.fetchall()]

print(f"\n[*] Tables found: {len(tables)}")
for table in tables:
    print(f"  - {table}")

# Inspect sensor_config
print("\n[*] sensor_config columns:")
cur.execute("PRAGMA table_info(sensor_config)")
for col in cur.fetchall():
    print(f"  {col[1]:30} {col[2]}")

# Inspect sensor_readings
print("\n[*] sensor_readings columns:")
cur.execute("PRAGMA table_info(sensor_readings)")
for col in cur.fetchall():
    print(f"  {col[1]:30} {col[2]}")

conn.close()
