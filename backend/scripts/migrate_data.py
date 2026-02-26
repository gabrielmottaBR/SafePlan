"""
SafePlan Backend - Data Migration from Legacy SQLite to New Database
Migrates sensors and readings from old safeplan.db to new backend database

Usage:
    cd backend
    python scripts/migrate_data.py --source ../path_to_backup/safeplan.db
"""

import sys
import os
import argparse
import logging
from pathlib import Path
from datetime import datetime

# Add parent directory (backend/) to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

from backend.src.data.database import get_session_factory, init_db, get_engine
from backend.src.data.models import SensorConfig, SensorReading
from backend.src.data.sensor_repository import SensorConfigRepository
from backend.src.data.reading_repository import SensorReadingRepository

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Suppress SQLAlchemy debug logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy.pool').setLevel(logging.WARNING)


def connect_legacy_db(path: str):
    """Connect to legacy SQLite database."""
    if not Path(path).exists():
        raise FileNotFoundError(f"Legacy database not found: {path}")
    
    engine = create_engine(f"sqlite:///{path}", echo=False)
    return engine


def migrate_sensors(legacy_engine, new_session) -> int:
    """Migrate sensor configurations from legacy to new database."""
    logger.info("[*] Migrating sensor configurations...")
    
    # Helper function to parse datetime - moved before function usage
    def parse_datetime(val):
        if val is None:
            return datetime.utcnow()
        if isinstance(val, datetime):
            return val
        if isinstance(val, str):
            # Try parse as ISO format
            if 'T' in val or ' ' in val:
                try:
                    # Handle ISO format or mysql format: 2026-02-22 17:36:50.430271
                    clean_val = val.replace('Z', '+00:00')
                    if '.' in clean_val:
                        # Has microseconds
                        return datetime.strptime(clean_val.split('+')[0], '%Y-%m-%d %H:%M:%S.%f')
                    else:
                        return datetime.strptime(clean_val.split('+')[0], '%Y-%m-%d %H:%M:%S')
                except Exception as ex:
                    logger.debug(f"Failed to parse datetime: {val}, error: {ex}")
                    return datetime.utcnow()
            return datetime.utcnow()
        return datetime.utcnow()
    
    # Query legacy sensors with correct column mapping
    with legacy_engine.connect() as conn:
        result = conn.execute(text("""
            SELECT 
                sensor_id,
                COALESCE(display_name, internal_name, 'Unknown') as name,
                COALESCE(descricao, '') as description,
                COALESCE(tipo_gas, sensor_type, 'Unknown') as sensor_type,
                COALESCE(uep, platform, 'Unknown') as location,
                COALESCE(unit, '') as unit,
                COALESCE(grupo, '') as grupo,
                COALESCE(modulo, '') as modulo,
                COALESCE(pi_server_tag, '') as pi_point_name,
                COALESCE(tipo_leitura, '') as pi_attribute_name,
                COALESCE(lower_warning_limit, 0) as alert_threshold_min,
                COALESCE(upper_critical_limit, 0) as alert_threshold_max,
                COALESCE(valor_pct, 0.85) as anomaly_threshold,
                COALESCE(valor_pct, 0) as valor_pct,
                COALESCE(enabled, 1) as is_active,
                COALESCE(created_at, datetime('now')) as created_at,
                COALESCE(updated_at, datetime('now')) as updated_at
            FROM sensor_config
        """))
        rows = result.fetchall()
    
    logger.info(f"[+] Found {len(rows)} sensors in legacy database")
    
    if not rows:
        return 0
    
    repo = SensorConfigRepository(new_session)
    migrated = 0
    batch = []
    
    for idx, row in enumerate(rows):
        try:
            created_at_str = row[15]
            updated_at_str = row[16]
            
            created_at = parse_datetime(created_at_str)
            updated_at = parse_datetime(updated_at_str)
            
            sensor_data = {
                'sensor_id': str(row[0]),
                'name': str(row[1])[:255],
                'description': str(row[2])[:500] if row[2] else '',
                'sensor_type': str(row[3])[:100],
                'location': str(row[4])[:100],
                'unit': str(row[5])[:50],
                'grupo': str(row[6])[:100] if row[6] else '',
                'modulo': str(row[7])[:100] if row[7] else '',
                'pi_point_name': str(row[8])[:255] if row[8] else '',
                'pi_attribute_name': str(row[9])[:100] if row[9] else '',
                'alert_threshold_min': float(row[10]) if row[10] else 0.0,
                'alert_threshold_max': float(row[11]) if row[11] else 0.0,
                'anomaly_threshold': float(row[12]) if row[12] else 0.85,
                'valor_pct': float(row[13]) if row[13] else 0.0,
                'is_active': bool(row[14]),
                'created_at': created_at,
                'updated_at': updated_at,
            }
            
            sensor = SensorConfig(**sensor_data)
            batch.append(sensor)
            
            if len(batch) >= 100:
                new_session.add_all(batch)
                new_session.commit()
                migrated += len(batch)
                logger.info(f"[+] Progress: {migrated} sensors migrated...")
                batch = []
                
        except Exception as e:
            logger.error(f"Error migrating sensor {row[0]}: {type(e).__name__}: {str(e)[:100]}")
            new_session.rollback()
            continue
    
    # Commit remaining batch
    if batch:
        new_session.add_all(batch)
        new_session.commit()
        migrated += len(batch)
    
    logger.info(f"[✓] Sensor migration complete: {migrated} sensors")
    return migrated


def migrate_readings(legacy_engine, new_session) -> int:
    """Migrate sensor readings from legacy to new database."""
    logger.info("[*] Migrating sensor readings...")
    
    # Helper function to parse datetime
    def parse_datetime(val):
        if val is None:
            return datetime.utcnow()
        if isinstance(val, datetime):
            return val
        if isinstance(val, str):
            try:
                return datetime.fromisoformat(val.replace('Z', '+00:00'))
            except:
                try:
                    return datetime.strptime(val, '%Y-%m-%d %H:%M:%S.%f')
                except:
                    return datetime.utcnow()
        return datetime.utcnow()
    
    # Query legacy readings
    with legacy_engine.connect() as conn:
        result = conn.execute(text("""
            SELECT 
                sensor_id, value, unit, timestamp, data_quality, fetched_at
            FROM sensor_readings
        """))
        rows = result.fetchall()
    
    logger.info(f"[+] Found {len(rows)} readings in legacy database")
    
    if not rows:
        return 0
    
    repo = SensorReadingRepository(new_session)
    migrated = 0
    batch = []
    
    # Map data quality codes
    quality_map = {
        1: "Good",
        0: "Bad",
        2: "Uncertain",
    }
    
    for row in rows:
        try:
            quality_code = quality_map.get(row[4], "Unknown")
            
            reading = SensorReading(
                sensor_id=str(row[0]),
                value=float(row[1]),
                unit=str(row[2])[:50] if row[2] else '',
                timestamp=parse_datetime(row[3]),
                quality_code=quality_code,
                source="PI Server",
                created_at=parse_datetime(row[5]),
            )
            batch.append(reading)
            
            if len(batch) >= 1000:
                new_session.add_all(batch)
                new_session.commit()
                migrated += len(batch)
                logger.info(f"[+] Progress: {migrated} readings migrated...")
                batch = []
                
        except Exception as e:
            logger.error(f"Error migrating reading for sensor {row[0]}: {e}")
            new_session.rollback()
            continue
    
    # Commit remaining batch
    if batch:
        new_session.add_all(batch)
        new_session.commit()
        migrated += len(batch)
    
    logger.info(f"[✓] Readings migration complete: {migrated} readings")
    return migrated


def main():
    """Run data migration."""
    parser = argparse.ArgumentParser(
        description="Migrate data from legacy SafePlan database to new backend database"
    )
    parser.add_argument(
        "--source",
        required=True,
        help="Path to legacy safeplan.db backup"
    )
    parser.add_argument(
        "--target",
        default="safeplan.db",
        help="Path to new backend database (default: safeplan.db)"
    )
    
    args = parser.parse_args()
    
    logger.info("=" * 70)
    logger.info("SafePlan Data Migration")
    logger.info("=" * 70)
    logger.info(f"Source: {args.source}")
    logger.info(f"Target: {args.target}\n")
    
    try:
        # Connect to legacy database
        legacy_engine = connect_legacy_db(args.source)
        logger.info(f"[✓] Connected to legacy database\n")
        
        # Initialize new database
        init_db()
        logger.info(f"[✓] New database initialized\n")
        
        # Create session for new database
        SessionLocal = get_session_factory()
        new_session = SessionLocal()
        
        # Run migrations
        sensors_migrated = migrate_sensors(legacy_engine, new_session)
        readings_migrated = migrate_readings(legacy_engine, new_session)
        
        new_session.close()
        
        # Summary
        logger.info("")
        logger.info("=" * 70)
        logger.info("[✓] MIGRATION COMPLETED")
        logger.info(f"    Sensors:  {sensors_migrated:>10,}")
        logger.info(f"    Readings: {readings_migrated:>10,}")
        logger.info(f"    Total:    {sensors_migrated + readings_migrated:>10,}")
        logger.info("=" * 70)
        
        return 0
    
    except Exception as e:
        logger.error(f"[!] Migration failed: {e}", exc_info=True)
        return 1
    
    finally:
        legacy_engine.dispose()


if __name__ == "__main__":
    sys.exit(main())

