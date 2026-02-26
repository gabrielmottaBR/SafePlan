#!/usr/bin/env python3
"""
Migration script with AUTOINCREMENT id column
"""
import sqlite3
from pathlib import Path

# Paths
import os
SCRIPT_DIR = Path(__file__).parent
BACKEND_DIR = SCRIPT_DIR.parent
SAFEPLAN_ROOT = BACKEND_DIR.parent
SOURCE_DB = SAFEPLAN_ROOT / "backups" / "backup_20260222_155523" / "safeplan.db"
TARGET_DB = BACKEND_DIR / "safeplan.db"

print(f"[*] Source: {SOURCE_DB}")
print(f"[*] Source exists: {SOURCE_DB.exists()}")
print(f"[*] Target: {TARGET_DB}")

print("[*] Migration with Proper ID Column")
print("=" * 60)

# Delete old database
if TARGET_DB.exists():
    TARGET_DB.unlink()
    print("[*] Deleted old database")

# Connect to source
source_conn = sqlite3.connect(str(SOURCE_DB))
source_conn.row_factory = sqlite3.Row
cur = source_conn.cursor()

# Connect to target
target_conn = sqlite3.connect(str(TARGET_DB))
tcur = target_conn.cursor()

# Create tables with proper schema
print("[*] Creating tables...")

# Create sensor_config table с autoincrement id
tcur.execute('''CREATE TABLE sensor_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sensor_id TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    description TEXT,
    sensor_type TEXT NOT NULL,
    location TEXT NOT NULL,
    unit TEXT,
    grupo TEXT,
    modulo TEXT,
    pi_point_name TEXT,
    pi_attribute_name TEXT,
    alert_threshold_min REAL,
    alert_threshold_max REAL,
    anomaly_threshold REAL,
    valor_pct REAL,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)''')

# Create sensor_reading table
tcur.execute('''CREATE TABLE sensor_reading (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sensor_id TEXT NOT NULL,
    value REAL,
    unit TEXT,
    timestamp TIMESTAMP,
    quality_code TEXT,
    source TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)''')

# Create alert tables (empty for now)
tcur.execute('''CREATE TABLE alert_rule (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sensor_id TEXT,
    rule_type TEXT,
    condition TEXT,
    threshold REAL,
    is_active INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)''')

tcur.execute('''CREATE TABLE alert_event (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sensor_id TEXT,
    alert_level TEXT,
    message TEXT,
    triggered_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)''')

tcur.execute('''CREATE TABLE anomaly_score (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sensor_id TEXT,
    score REAL,
    timestamp TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)''')

tcur.execute('''CREATE TABLE forecast (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sensor_id TEXT,
    predicted_value REAL,
    forecast_time TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)''')

print("[OK] Schema created")

# Migrate sensors
print("[*] Migrating sensors...")
cur.execute('''SELECT COUNT(*) FROM sensor_config''')
total_sensors = cur.fetchone()[0]
print(f"[+] Found {total_sensors} sensors in source")

cur.execute('''SELECT sensor_id, 
              COALESCE(display_name, internal_name, 'Unknown'),
              COALESCE(descricao, ''),
              sensor_type,
              uep,
              COALESCE(unit, ''),
              COALESCE(tipo_gas, ''),
              COALESCE(modulo, ''),
              COALESCE(pi_server_tag, ''),
              'Valor Atual'
              FROM sensor_config''')

migrated_sensors = 0
for i, row in enumerate(cur.fetchall()):
    try:
        tcur.execute('''INSERT INTO sensor_config 
                       (sensor_id, name, description, sensor_type, location, unit, grupo, modulo,
                        pi_point_name, pi_attribute_name, alert_threshold_min, alert_threshold_max,
                        anomaly_threshold, valor_pct, is_active, created_at, updated_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))''',
                    (str(row[0])[:100], str(row[1])[:255], str(row[2])[:500], str(row[3])[:100], 
                     str(row[4])[:255], str(row[5])[:20], str(row[6])[:50], str(row[7])[:50],
                     str(row[8])[:255], str(row[9])[:255], 0.0, 0.0, 0.85, 0.0, 1))
        migrated_sensors += 1
        if (i+1) % 1000 == 0:
            target_conn.commit()
            print(f'[+] {migrated_sensors} sensors...')
    except Exception as e:
        print(f'    Error on sensor {row[0]}: {type(e).__name__}')
        continue

target_conn.commit()
print(f'[DONE] {migrated_sensors} sensors migrated')

# Migrate readings
print('[*] Migrating readings...')
cur.execute('SELECT COUNT(*) FROM sensor_readings')
total_readings = cur.fetchone()[0]
print(f'[+] Found {total_readings} readings in source')

cur.execute('''SELECT sensor_id, value, unit, timestamp, data_quality, fetched_at FROM sensor_readings''')

quality_map = {1: 'Good', 0: 'Bad', 2: 'Uncertain'}
migrated_readings = 0

for i, row in enumerate(cur.fetchall()):
    try:
        quality_str = quality_map.get(int(row[4]) if row[4] else 0, 'Uncertain')
        tcur.execute('''INSERT INTO sensor_reading 
                       (sensor_id, value, unit, timestamp, quality_code, source, created_at)
                       VALUES (?, ?, ?, ?, ?, ?, COALESCE(?, datetime('now')))''',
                    (str(row[0])[:100], float(row[1]) if row[1] else 0.0, str(row[2])[:20],
                     row[3], quality_str, 'legacy_import', row[5]))
        migrated_readings += 1
        if (i+1) % 5000 == 0:
            target_conn.commit()
            print(f'[+] {migrated_readings} readings...')
    except Exception as e:
        print(f'    Error on reading {i}: {type(e).__name__}: {e}')
        continue

target_conn.commit()
print(f'[DONE] {migrated_readings} readings migrated')

# Verify
print('\n[*] Verification...')
tcur.execute('SELECT COUNT(*) FROM sensor_config')
sensor_count = tcur.fetchone()[0]
tcur.execute('SELECT COUNT(*) FROM sensor_reading')
reading_count = tcur.fetchone()[0]

print(f'[OK] sensor_config: {sensor_count} rows')
print(f'[OK] sensor_reading: {reading_count} rows')

# Close connections
source_conn.close()
target_conn.close()

print("\n" + "=" * 60)
print("[DONE] MIGRATION COMPLETED")
print(f"    Sensors:       {sensor_count:,}")
print(f"    Readings:      {reading_count:,}")
print("=" * 60)
print(f"[OK] Database ready at: {TARGET_DB}")
