"""
Script para popular dados de teste de leituras de sensores.
Cria leituras fictícias recentes para todos os sensores no banco.
"""
import logging
import random
from datetime import datetime, timedelta
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.database import DatabaseManager
from src.data.models import SensorConfig, SensorReading

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def populate_test_readings(num_readings_per_sensor: int = 5, hours_back: int = 24):
    """
    Populate database with test readings for all sensors.
    
    Args:
        num_readings_per_sensor: Number of readings to create per sensor
        hours_back: How many hours back to generate readings from
    """
    db = DatabaseManager()
    session = db.get_session()
    
    try:
        # Get all sensors
        sensors = session.query(SensorConfig).all()
        total_sensors = len(sensors)
        
        if total_sensors == 0:
            logger.warning("No sensors found in database")
            return
        
        logger.info(f"Found {total_sensors} sensors")
        logger.info(f"Generating {num_readings_per_sensor} readings per sensor...")
        
        readings_created = 0
        now = datetime.utcnow()
        
        for sensor_idx, sensor in enumerate(sensors, 1):
            if sensor_idx % 500 == 0:
                logger.info(f"  Processing sensor {sensor_idx}/{total_sensors}...")
            
            # Generate N readings spread over time
            for reading_idx in range(num_readings_per_sensor):
                # Distribute readings evenly over the time window
                minutes_ago = (hours_back * 60) * (reading_idx / (num_readings_per_sensor - 1)) if num_readings_per_sensor > 1 else 0
                timestamp = now - timedelta(minutes=minutes_ago)
                
                # Generate realistic value based on sensor type
                if sensor.tipo_gas == 'O2':
                    # O2 sensors typically read 0-25%
                    value = random.gauss(20.5, 1.5)
                    value = max(0, min(100, value))  # Clamp 0-100
                elif sensor.tipo_gas in ['CH4', 'CO2', 'H2S']:
                    # Gas sensors typically read 0-100%
                    value = random.gauss(15.0, 8.0)
                    value = max(0, min(100, value))  # Clamp 0-100
                elif sensor.tipo_gas == 'FLAME':
                    # FLAME detectors: 0-100%
                    value = random.choice([0, 0, 0, 10, 20])  # Usually 0, occasionally higher
                else:
                    # Default: 0-50%
                    value = random.gauss(25.0, 12.0)
                    value = max(0, min(100, value))  # Clamp 0-100
                
                # Create reading
                reading = SensorReading(
                    sensor_id=sensor.sensor_id,
                    value=round(value, 2),
                    timestamp=timestamp,
                    unit=sensor.unit,
                    data_quality=0  # Good quality
                )
                session.add(reading)
                readings_created += 1
        
        # Commit all readings
        session.commit()
        logger.info(f"✓ Created {readings_created} test readings")
        logger.info(f"  Total: {total_sensors} sensors x {num_readings_per_sensor} readings each")
        
    except Exception as e:
        logger.error(f"Error populating readings: {e}")
        session.rollback()
        raise
    finally:
        session.close()


def populate_sensor_valor_pct(default_value: float = 0.0):
    """
    Set default valor_pct for all sensors (if NULL).
    This is a fallback value - actual values should come from readings.
    """
    db = DatabaseManager()
    session = db.get_session()
    
    try:
        # Find sensors with NULL valor_pct
        null_sensors = session.query(SensorConfig).filter(
            SensorConfig.valor_pct == None
        ).all()
        
        logger.info(f"Found {len(null_sensors)} sensors with NULL valor_pct")
        
        for sensor in null_sensors:
            # Set a default value based on sensor type
            if sensor.tipo_gas == 'O2':
                sensor.valor_pct = 20.5  # Typical O2 level
            elif sensor.tipo_gas in ['CH4', 'CO2', 'H2S']:
                sensor.valor_pct = 0.0  # Safe level
            else:
                sensor.valor_pct = default_value
        
        session.commit()
        logger.info(f"✓ Set default valor_pct for {len(null_sensors)} sensors")
        
    except Exception as e:
        logger.error(f"Error updating valor_pct: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    import sys
    
    logger.info("=" * 70)
    logger.info("POPULATE TEST READINGS")
    logger.info("=" * 70)
    logger.info("This script creates test sensor readings in the database")
    logger.info("Useful for development and testing without PI AF connection")
    logger.info("")
    
    # Populate readings
    populate_test_readings(num_readings_per_sensor=10, hours_back=24)
    
    # Set default valor_pct values
    populate_sensor_valor_pct(default_value=0.0)
    
    logger.info("")
    logger.info("=" * 70)
    logger.info("TEST DATA POPULATION COMPLETE")
    logger.info("=" * 70)
