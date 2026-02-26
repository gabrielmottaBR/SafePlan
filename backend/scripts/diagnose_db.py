#!/usr/bin/env python3
"""
Diagnóstico rápido do banco de dados
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, inspect, text
from backend.src.data.models import Base, SensorConfig
from backend.config.settings import get_settings

print("[*] SafePlan Database Diagnostics")
print("=" * 60)

settings = get_settings()
engine = create_engine(settings.database_url, echo=False)

print(f"[*] Database URL: {settings.database_url}")

# Check if tables exist
inspector = inspect(engine)
tables = inspector.get_table_names()
print(f"\n[*] Tables in database: {tables}")

# Check sensor_config structure
if 'sensor_config' in tables:
    print("\n[*] sensor_config columns:")
    columns = inspector.get_columns('sensor_config')
    for col in columns:
        print(f"    - {col['name']:25} {col['type']}")
    
    # Try raw SQL count
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM sensor_config"))
        count = result.scalar()
        print(f"\n[+] Raw SQL count: {count} rows")

# Try SQL Alchemy ORM count
try:
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=engine)
    session = Session()
    
    count = session.query(SensorConfig).count()
    print(f"[+] SQLAlchemy ORM count: {count} rows")
    
    # Try fetching one row
    sensor = session.query(SensorConfig).limit(1).first()
    if sensor:
        print(f"\n[+] Sample sensor:")
        print(f"    ID: {sensor.id}")
        print(f"    Sensor ID: {sensor.sensor_id}")
        print(f"    Name: {sensor.name}")
        print(f"    Type: {sensor.sensor_type}")
    
    session.close()
    print("\n[OK] SQLAlchemy ORM working correctly")
except Exception as e:
    print(f"\n[ERROR] SQLAlchemy ORM failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
