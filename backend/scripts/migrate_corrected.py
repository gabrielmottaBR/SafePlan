#!/usr/bin/env python
"""Corrected migration: Create schema with SQLAlchemy, then migrate data"""
import sqlite3
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

source = '../backups/backup_20260222_155523/safeplan.db'
target = 'safeplan.db'

print('[*] Corrected Migration with SQLAlchemy Schema')
print('=' * 60)

# Remove old database
if os.path.exists(target):
    os.remove(target)
    print('[*] Deleted old safeplan.db')

# Initialize database with SQLAlchemy models
print('[*] Creating tables with SQLAlchemy...')
from sqlalchemy import create_engine
from backend.src.data.models import Base

# Create engine for target database
target_engine = create_engine(f'sqlite:///{target}')

# Create all tables
Base.metadata.create_all(bind=target_engine)
print('[OK] Database schema created')

# Now migrate data
print('[*] Migrating data from legacy database...')

source_conn = sqlite3.connect(source)
target_conn = sqlite3.connect(target)

# Migrate sensors
print('[*] Migrating sensors...')
cur = source_conn.cursor()
cur.execute('SELECT COUNT(*) FROM sensor_config')
total_sensors = cur.fetchone()[0]
print(f'[+] Found {total_sensors} sensors in source')

cur.execute('''SELECT sensor_id, COALESCE(display_name, internal_name, 'Unknown') as name,
              COALESCE(descricao, '') as desc, COALESCE(tipo_gas, sensor_type, 'Gas') as type,
              COALESCE(uep, platform, 'Unknown') as location, COALESCE(unit, '') as unit,
              COALESCE(grupo, '') as grupo, COALESCE(modulo, '') as modulo,
              COALESCE(pi_server_tag, '') as pi_point_name, COALESCE(tipo_leitura, '') as pi_attr
              FROM sensor_config''')

rows = cur.fetchall()
tcur = target_conn.cursor()

migrated_sensors = 0
for i, row in enumerate(rows):
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

for row in cur:
    try:
        quality = quality_map.get(row[4], 'Unknown')
        tcur.execute('''INSERT INTO sensor_reading
                       (sensor_id, value, unit, timestamp, quality_code, source, created_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?)''',
                    (str(row[0])[:100], float(row[1]) if row[1] else 0.0, str(row[2])[:20] if row[2] else '', 
                     row[3], quality, 'PI Server', row[5] if row[5] else 'now'))
        migrated_readings += 1
        if migrated_readings % 5000 == 0:
            target_conn.commit()
            print(f'[+] {migrated_readings} readings...')
    except Exception as e:
        if migrated_readings % 50000 == 0:
            print(f'    Skipping reading: {type(e).__name__}')
        continue

target_conn.commit()
print(f'[DONE] {migrated_readings} readings migrated')

source_conn.close()
target_conn.close()

# Verify data
print('')
print('=' * 60)
print('[DONE] MIGRATION COMPLETED')
print(f'    Sensors:  {migrated_sensors:>10,}')
print(f'    Readings: {migrated_readings:>10,}')
print('=' * 60)
print('')

# Quick verification query
verify_conn = sqlite3.connect(target)
vcur = verify_conn.cursor()
vcur.execute('SELECT COUNT(*) FROM sensor_config')
count = vcur.fetchone()[0]
print(f'[OK] Verification: sensor_config table has {count} rows')
vcur.execute('SELECT COUNT(*) FROM sensor_reading')
count = vcur.fetchone()[0]
print(f'[OK] Verification: sensor_reading table has {count} rows')
verify_conn.close()

print(f'[OK] Database ready at: {target}')
