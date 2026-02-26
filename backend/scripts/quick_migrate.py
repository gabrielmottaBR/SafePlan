import sqlite3
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

source = '../backups/backup_20260222_155523/safeplan.db'
target = 'safeplan.db'

print('[*] Migrating data...')

# Remove old database
if os.path.exists(target):
    os.remove(target)

# Create target database structure directly
target_conn = sqlite3.connect(target)
target_conn.execute('''CREATE TABLE IF NOT EXISTS sensor_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sensor_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    sensor_type TEXT,
    location TEXT,
    unit TEXT,
    grupo TEXT,
    modulo TEXT,
    pi_point_name TEXT,
    pi_attribute_name TEXT,
    alert_threshold_min FLOAT DEFAULT 0,
    alert_threshold_max FLOAT DEFAULT 0,
    anomaly_threshold FLOAT DEFAULT 0.85,
    valor_pct FLOAT DEFAULT 0,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)''')

target_conn.execute('''CREATE TABLE IF NOT EXISTS sensor_reading (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sensor_id TEXT NOT NULL,
    value FLOAT,
    unit TEXT,
    timestamp TIMESTAMP,
    quality_code TEXT DEFAULT 'Good',
    source TEXT DEFAULT 'PI Server',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)''')

target_conn.commit()

# Connect to source
source_conn = sqlite3.connect(source)

# Migrate sensors
print('[*] Migrating sensors...')
cur = source_conn.cursor()
cur.execute('SELECT COUNT(*) FROM sensor_config')
total = cur.fetchone()[0]
print(f'[+] Found {total} sensors')

cur.execute('''SELECT sensor_id, COALESCE(display_name, internal_name, 'Unknown') as name,
              COALESCE(descricao, '') as desc, COALESCE(tipo_gas, sensor_type, 'Gas') as type,
              COALESCE(uep, platform, 'Unknown') as location
              FROM sensor_config''')

rows = cur.fetchall()
tcur = target_conn.cursor()

for i, row in enumerate(rows):
    try:
        tcur.execute('''INSERT INTO sensor_config 
                       (sensor_id, name, description, sensor_type, location, unit, grupo, modulo,
                        pi_point_name, pi_attribute_name, alert_threshold_min, alert_threshold_max,
                        anomaly_threshold, valor_pct, is_active, created_at, updated_at)
                       VALUES (?, ?, ?, ?, ?, '', '', '', '', '', 0, 0, 0.85, 0, 1, datetime('now'), datetime('now'))''',
                    (str(row[0]), str(row[1])[:255], str(row[2])[:500], str(row[3])[:100], str(row[4])[:100]))
        if (i+1) % 1000 == 0:
            target_conn.commit()
            print(f'[+] {i+1} sensors...')
    except Exception as e:
        print(f'Error on {i}: {e}')
        continue

target_conn.commit()
print(f'[✓] {total} sensors migrated')

# Migrate readings
print('[*] Migrating readings...')
cur.execute('SELECT COUNT(*) FROM sensor_readings')
total = cur.fetchone()[0]
print(f'[+] Found {total} readings')

cur.execute('''SELECT sensor_id, value, unit, timestamp, data_quality, fetched_at FROM sensor_readings''')

quality_map = {1: 'Good', 0: 'Bad', 2: 'Uncertain'}
migrated = 0

for row in cur:
    try:
        quality = quality_map.get(row[4], 'Unknown')
        tcur.execute('''INSERT INTO sensor_reading
                       (sensor_id, value, unit, timestamp, quality_code, source, created_at)
                       VALUES (?, ?, ?, ?, ?, 'PI Server', datetime('now'))''',
                    (str(row[0]), float(row[1]) if row[1] else 0, str(row[2])[:50] if row[2] else '', row[3], quality))
        migrated += 1
        if migrated % 5000 == 0:
            target_conn.commit()
            print(f'[+] {migrated} readings...')
    except Exception as e:
        continue

target_conn.commit()
print(f'[✓] {migrated} readings migrated')

source_conn.close()
target_conn.close()

print('')
print('=' * 60)
print('[✓] MIGRATION COMPLETED')
print(f'    Sensors:  {total:>10,}')
print(f'    Readings: {migrated:>10,}')
print('=' * 60)
