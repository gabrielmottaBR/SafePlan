"""
SafePlan Backend - Sensor Reading Repository
CRUD operations for sensor readings
"""

from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.src.data.base_repository import BaseRepository
from backend.src.data.models import SensorReading


class SensorReadingRepository(BaseRepository[SensorReading]):
    """
    Repository for SensorReading CRUD operations.
    """
    
    def __init__(self, db: Session):
        """Initialize with session."""
        super().__init__(db, SensorReading)
    
    def get_latest_by_sensor(self, sensor_id: str) -> Optional[SensorReading]:
        """
        Get latest reading for a sensor.
        
        Args:
            sensor_id: Sensor identifier
            
        Returns:
            Latest SensorReading or None
        """
        return self.db.query(SensorReading).filter(
            SensorReading.sensor_id == sensor_id
        ).order_by(desc(SensorReading.timestamp)).first()
    
    def get_range(
        self,
        sensor_id: str,
        start_time: datetime,
        end_time: datetime
    ) -> List[SensorReading]:
        """
        Get readings within time range.
        
        Args:
            sensor_id: Sensor identifier
            start_time: Start datetime
            end_time: End datetime
            
        Returns:
            List of readings in range
        """
        return self.db.query(SensorReading).filter(
            SensorReading.sensor_id == sensor_id,
            SensorReading.timestamp >= start_time,
            SensorReading.timestamp <= end_time
        ).order_by(SensorReading.timestamp).all()
    
    def get_last_n_readings(
        self,
        sensor_id: str,
        n: int = 100
    ) -> List[SensorReading]:
        """
        Get last N readings for a sensor.
        
        Args:
            sensor_id: Sensor identifier
            n: Number of readings
            
        Returns:
            List of last N readings
        """
        return self.db.query(SensorReading).filter(
            SensorReading.sensor_id == sensor_id
        ).order_by(desc(SensorReading.timestamp)).limit(n).all()
    
    def get_last_hours(
        self,
        sensor_id: str,
        hours: int = 24
    ) -> List[SensorReading]:
        """
        Get readings from last N hours.
        
        Args:
            sensor_id: Sensor identifier
            hours: Number of hours back
            
        Returns:
            List of readings from last N hours
        """
        start_time = datetime.utcnow() - timedelta(hours=hours)
        return self.get_range(sensor_id, start_time, datetime.utcnow())
    
    def get_by_quality(
        self,
        sensor_id: str,
        quality_code: str
    ) -> List[SensorReading]:
        """
        Get readings by quality code.
        
        Args:
            sensor_id: Sensor identifier
            quality_code: Quality code (Good, Uncertain, Bad)
            
        Returns:
            List of readings with quality code
        """
        return self.db.query(SensorReading).filter(
            SensorReading.sensor_id == sensor_id,
            SensorReading.quality_code == quality_code
        ).all()
    
    def get_statistics(
        self,
        sensor_id: str,
        hours: int = 24
    ) -> dict:
        """
        Get statistics for sensor readings.
        
        Args:
            sensor_id: Sensor identifier
            hours: Time window in hours
            
        Returns:
            Dict with min, max, avg, count
        """
        from sqlalchemy import func
        
        start_time = datetime.utcnow() - timedelta(hours=hours)
        result = self.db.query(
            func.min(SensorReading.value).label("min_value"),
            func.max(SensorReading.value).label("max_value"),
            func.avg(SensorReading.value).label("avg_value"),
            func.count(SensorReading.id).label("count")
        ).filter(
            SensorReading.sensor_id == sensor_id,
            SensorReading.timestamp >= start_time
        ).first()
        
        return {
            "min": result.min_value,
            "max": result.max_value,
            "avg": result.avg_value,
            "count": result.count,
        }
    
    def create_bulk(self, readings_list: List[dict]) -> int:
        """
        Create multiple readings in one transaction.
        
        Args:
            readings_list: List of reading dicts
            
        Returns:
            Number of readings created
        """
        objects = [SensorReading(**r) for r in readings_list]
        self.db.add_all(objects)
        self.db.commit()
        return len(objects)
    
    def delete_older_than(self, days: int) -> int:
        """
        Delete readings older than N days.
        
        Args:
            days: Age threshold in days
            
        Returns:
            Number of deleted readings
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        count = self.db.query(SensorReading).filter(
            SensorReading.timestamp < cutoff_date
        ).delete()
        self.db.commit()
        return count
