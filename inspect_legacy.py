"""Inspect legacy database schema."""
from sqlalchemy import create_engine, text

legacy_db = create_engine('sqlite:///backups/backup_20260222_155523/safeplan.db')

with legacy_db.connect() as conn:
    # List tables
    result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
    tables = [row[0] for row in result]
    print('[*] Tables in legacy database:')
    for table in tables:
        print(f'  - {table}')
    
    print()
    
    # Get sensor_config structure
    if 'sensor_config' in tables:
        print('[*] sensor_config columns:')
        result = conn.execute(text('PRAGMA table_info(sensor_config)'))
        for row in result:
            print(f'  {row[1]:30} {row[2]}')
    
    print()
    
    # Get sensor_readings structure
    if 'sensor_readings' in tables:
        print('[*] sensor_readings columns:')
        result = conn.execute(text('PRAGMA table_info(sensor_readings)'))
        for row in result:
            print(f'  {row[1]:30} {row[2]}')
    
    print()
    
    # Count records
    if 'sensor_config' in tables:
        result = conn.execute(text('SELECT COUNT(*) FROM sensor_config'))
        count = result.scalar()
        print(f'[*] Total sensor_config records: {count}')
    
    if 'sensor_readings' in tables:
        result = conn.execute(text('SELECT COUNT(*) FROM sensor_readings'))
        count = result.scalar()
        print(f'[*] Total sensor_readings records: {count}')
