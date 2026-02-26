#!/usr/bin/env python
"""Simple migration using raw SQL inserts"""
import sys
import os
import logging
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import create_engine, text

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def migrate_simple(source_db, target_db):
    """Simple migration using SQL inserts."""
    
    # Connect to source
    source_engine = create_engine(f'sqlite:///{source_db}')
    target_engine = create_engine(f'sqlite:///{target_db}')
    
    logger.info(f"[*] Copying sensors from {source_db}...")
    
    with source_engine.connect() as src_conn:
        with target_engine.connect() as tgt_conn:
            # Copy sensors
            result = src_conn.execute(text("""
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
                    0.85 as anomaly_threshold,
                    COALESCE(valor_pct, 0) as valor_pct,
                    COALESCE(enabled, 1) as is_active,
                    COALESCE(created_at, datetime('2026-02-22')) as created_at,
                    COALESCE(updated_at, datetime('2026-02-22')) as updated_at
                FROM sensor_config
            """))
            rows = result.fetchall()
            
            migrated = 0
            for row in rows:
                try:
                    tgt_conn.execute(text("""
                        INSERT INTO sensor_config 
                        (sensor_id, name, description, sensor_type, location, unit, grupo, modulo,
                         pi_point_name, pi_attribute_name, alert_threshold_min, alert_threshold_max,
                         anomaly_threshold, valor_pct, is_active, created_at, updated_at)
                        VALUES (:sid, :name, :desc, :type, :loc, :unit, :grupo, :modulo,
                                :pi_point, :pi_attr, :thresh_min, :thresh_max,
                                :anomaly, :valor, :active, :created, :updated)
                    """), {
                        'sid': str(row[0]),
                        'name': str(row[1])[:255] if row[1] else 'Unknown',
                        'desc': str(row[2])[:500] if row[2] else '',
                        'type': str(row[3])[:100] if row[3] else 'Unknown',
                        'loc': str(row[4])[:100] if row[4] else 'Unknown',
                        'unit': str(row[5])[:50] if row[5] else '',
                        'grupo': str(row[6])[:100] if row[6] else '',
                        'modulo': str(row[7])[:100] if row[7] else '',
                        'pi_point': str(row[8])[:255] if row[8] else '',
                        'pi_attr': str(row[9])[:100] if row[9] else '',
                        'thresh_min': float(row[10]) if row[10] else 0.0,
                        'thresh_max': float(row[11]) if row[11] else 0.0,
                        'anomaly': float(row[12]) if row[12] else 0.85,
                        'valor': float(row[13]) if row[13] else 0.0,
                        'active': bool(row[14]),
                        'created': row[15],
                        'updated': row[16],
                    })
                    migrated += 1
                    if migrated % 500 == 0:
                        tgt_conn.commit()
                        logger.info(f"[+] {migrated} sensors...")
                except Exception as e:
                    logger.error(f"Error on sensor {row[0]}: {e}")
                    continue
            
            tgt_conn.commit()
            logger.info(f"[✓] Sensors: {migrated}")
            
            # Copy readings
            logger.info(f"[*] Copying readings...")
            result = src_conn.execute(text("""
                SELECT sensor_id, value, unit, timestamp, data_quality, fetched_at
                FROM sensor_readings
            """))
            
            readings = 0
            quality_map = {1: "Good", 0: "Bad", 2: "Uncertain"}
            
            for row in result:
                try:
                    quality = quality_map.get(row[4], "Unknown")
                    tgt_conn.execute(text("""
                        INSERT INTO sensor_reading 
                        (sensor_id, value, unit, timestamp, quality_code, source, created_at)
                        VALUES (:sid, :val, :unit, :ts, :quality, :source, :created)
                    """), {
                        'sid': str(row[0]),
                        'val': float(row[1]),
                        'unit': str(row[2])[:50] if row[2] else '',
                        'ts': row[3],
                        'quality': quality,
                        'source': 'PI Server',
                        'created': row[5],
                    })
                    readings += 1
                    if readings % 5000 == 0:
                        tgt_conn.commit()
                        logger.info(f"[+] {readings} readings...")
                except Exception as e:
                    logger.error(f"Error on reading: {e}")
                    continue
            
            tgt_conn.commit()
            logger.info(f"[✓] Readings: {readings}")
            logger.info(f"\n[✓] MIGRATION COMPLETE")
            logger.info(f"    Sensors:  {migrated:>10,}")
            logger.info(f"    Readings: {readings:>10,}")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', required=True, help='Source database')
    parser.add_argument('--target', default='safeplan.db', help='Target database')
    
    args = parser.parse_args()
    
    try:
        migrate_simple(args.source, args.target)
    except Exception as e:
        logger.error(f"Migration failed: {e}", exc_info=True)
        sys.exit(1)
