"""
SafePlan Backend - Sensor Configuration Repository
CRUD operations for sensor management
"""

from typing import List, Optional
from sqlalchemy.orm import Session

from backend.src.data.base_repository import BaseRepository
from backend.src.data.models import SensorConfig


class SensorConfigRepository(BaseRepository[SensorConfig]):
    """
    Repository for SensorConfig CRUD operations.
    """
    
    def __init__(self, db: Session):
        """Initialize with session."""
        super().__init__(db, SensorConfig)
    
    def get_by_sensor_id(self, sensor_id: str) -> Optional[SensorConfig]:
        """
        Get sensor by sensor_id.
        
        Args:
            sensor_id: Unique sensor identifier
            
        Returns:
            SensorConfig or None
        """
        return self.db.query(SensorConfig).filter(
            SensorConfig.sensor_id == sensor_id
        ).first()
    
    def get_by_location(self, location: str) -> List[SensorConfig]:
        """
        Get all sensors by location.
        
        Args:
            location: Location name
            
        Returns:
            List of sensors at location
        """
        return self.db.query(SensorConfig).filter(
            SensorConfig.location == location
        ).all()
    
    def get_by_type(self, sensor_type: str) -> List[SensorConfig]:
        """
        Get all sensors by type.
        
        Args:
            sensor_type: Sensor type (O2, CH4, etc)
            
        Returns:
            List of sensors of type
        """
        return self.db.query(SensorConfig).filter(
            SensorConfig.sensor_type == sensor_type
        ).all()
    
    def get_by_group(self, grupo: str) -> List[SensorConfig]:
        """
        Get all sensors in a voting group.
        
        Args:
            grupo: Group identifier (ex: 10S_FD)
            
        Returns:
            List of sensors in group
        """
        return self.db.query(SensorConfig).filter(
            SensorConfig.grupo == grupo
        ).all()
    
    def get_by_module(self, modulo: str) -> List[SensorConfig]:
        """
        Get all sensors in a module.
        
        Args:
            modulo: Module identifier (ex: 10S)
            
        Returns:
            List of sensors in module
        """
        return self.db.query(SensorConfig).filter(
            SensorConfig.modulo == modulo
        ).all()
    
    def get_active(self, skip: int = 0, limit: int = 100) -> List[SensorConfig]:
        """
        Get only active sensors.
        
        Args:
            skip: Records to skip
            limit: Max records
            
        Returns:
            List of active sensors
        """
        return self.db.query(SensorConfig).filter(
            SensorConfig.is_active == True
        ).offset(skip).limit(limit).all()
    
    def get_with_alert_threshold(self) -> List[SensorConfig]:
        """
        Get sensors with alert thresholds configured.
        
        Returns:
            List of sensors with threshold
        """
        return self.db.query(SensorConfig).filter(
            (SensorConfig.alert_threshold_min.isnot(None)) |
            (SensorConfig.alert_threshold_max.isnot(None))
        ).all()
    
    def count_by_type(self) -> dict:
        """
        Count sensors by type.
        
        Returns:
            Dict with sensor_type: count
        """
        from sqlalchemy import func
        
        results = self.db.query(
            SensorConfig.sensor_type,
            func.count(SensorConfig.id)
        ).group_by(SensorConfig.sensor_type).all()
        
        return {sensor_type: count for sensor_type, count in results}
    
    def count_by_location(self) -> dict:
        """
        Count sensors by location.
        
        Returns:
            Dict with location: count
        """
        from sqlalchemy import func
        
        results = self.db.query(
            SensorConfig.location,
            func.count(SensorConfig.id)
        ).group_by(SensorConfig.location).all()
        
        return {location: count for location, count in results}
    
    def update_valor_pct(self, sensor_id: str, valor_pct: float) -> bool:
        """
        Update valor_pct for a sensor.
        
        Args:
            sensor_id: Sensor identifier
            valor_pct: New valor percentage
            
        Returns:
            True if updated, False if not found
        """
        sensor = self.get_by_sensor_id(sensor_id)
        if sensor:
            sensor.valor_pct = valor_pct
            self.db.commit()
            return True
        return False
    
    def get_by_grupo(self, grupo: str, skip: int = 0, limit: int = 100) -> List[SensorConfig]:
        """
        Get all sensors in a voting group (grupo).
        
        Args:
            grupo: Voting group identifier (ex: 10S_FD, CH4, FLAME)
            skip: Records to skip
            limit: Max records
            
        Returns:
            List of sensors in grupo
        """
        return self.db.query(SensorConfig).filter(
            SensorConfig.grupo == grupo
        ).offset(skip).limit(limit).all()
    
    def get_by_modulo(self, modulo: str, skip: int = 0, limit: int = 100) -> List[SensorConfig]:
        """
        Get all sensors in a module/platform (módulo).
        
        Args:
            modulo: Module/platform identifier (ex: 10S, HULL, M05)
            skip: Records to skip
            limit: Max records
            
        Returns:
            List of sensors in módulo
        """
        return self.db.query(SensorConfig).filter(
            SensorConfig.modulo == modulo
        ).offset(skip).limit(limit).all()
    
    def get_grupos(self) -> List[str]:
        """
        Get all unique grupos.
        
        Returns:
            List of unique grupo values
        """
        from sqlalchemy import func
        
        result = self.db.query(SensorConfig.grupo).filter(
            SensorConfig.grupo.isnot(None)
        ).distinct().order_by(SensorConfig.grupo).all()
        
        return [row[0] for row in result]
    
    def get_modulos(self) -> List[str]:
        """
        Get all unique módulos.
        
        Returns:
            List of unique modulo values
        """
        from sqlalchemy import func
        
        result = self.db.query(SensorConfig.modulo).filter(
            SensorConfig.modulo.isnot(None)
        ).distinct().order_by(SensorConfig.modulo).all()
        
        return [row[0] for row in result]
    
    def count_by_grupo(self) -> dict:
        """
        Count sensors by voting group.
        
        Returns:
            Dict with grupo: count
        """
        from sqlalchemy import func
        
        results = self.db.query(
            SensorConfig.grupo,
            func.count(SensorConfig.id)
        ).filter(SensorConfig.grupo.isnot(None)).group_by(SensorConfig.grupo).all()
        
        return {grupo: count for grupo, count in results}
    
    def count_by_modulo(self) -> dict:
        """
        Count sensors by module/platform.
        
        Returns:
            Dict with modulo: count
        """
        from sqlalchemy import func
        
        results = self.db.query(
            SensorConfig.modulo,
            func.count(SensorConfig.id)
        ).filter(SensorConfig.modulo.isnot(None)).group_by(SensorConfig.modulo).all()
        
        return {modulo: count for modulo, count in results}
