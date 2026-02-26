"""
SafePlan Backend - Alert Repository
CRUD operations for alert rules and events
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_

from backend.src.data.base_repository import BaseRepository
from backend.src.data.models import AlertRule, AlertEvent


class AlertRuleRepository(BaseRepository[AlertRule]):
    """
    Repository for AlertRule CRUD operations.
    """
    
    def __init__(self, db: Session):
        """Initialize with session."""
        super().__init__(db, AlertRule)
    
    def get_by_sensor(self, sensor_id: str) -> List[AlertRule]:
        """
        Get all alert rules for a sensor.
        
        Args:
            sensor_id: Sensor identifier
            
        Returns:
            List of alert rules
        """
        return self.db.query(AlertRule).filter(
            AlertRule.sensor_id == sensor_id
        ).all()
    
    def get_active_by_sensor(self, sensor_id: str) -> List[AlertRule]:
        """
        Get active alert rules for a sensor.
        
        Args:
            sensor_id: Sensor identifier
            
        Returns:
            List of active alert rules
        """
        return self.db.query(AlertRule).filter(
            AlertRule.sensor_id == sensor_id,
            AlertRule.is_active == True
        ).all()
    
    def get_by_level(self, alert_level: str) -> List[AlertRule]:
        """
        Get rules by alert level.
        
        Args:
            alert_level: Alert level (Info, Warning, Critical)
            
        Returns:
            List of rules with this level
        """
        return self.db.query(AlertRule).filter(
            AlertRule.alert_level == alert_level
        ).all()
    
    def get_active(self, skip: int = 0, limit: int = 100) -> List[AlertRule]:
        """
        Get all active alert rules.
        
        Args:
            skip: Records to skip
            limit: Max records
            
        Returns:
            List of active rules
        """
        return self.db.query(AlertRule).filter(
            AlertRule.is_active == True
        ).offset(skip).limit(limit).all()


class AlertEventRepository(BaseRepository[AlertEvent]):
    """
    Repository for AlertEvent CRUD operations (read-mostly).
    """
    
    def __init__(self, db: Session):
        """Initialize with session."""
        super().__init__(db, AlertEvent)
    
    def get_by_sensor(
        self,
        sensor_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[AlertEvent]:
        """
        Get alert events for a sensor.
        
        Args:
            sensor_id: Sensor identifier
            skip: Records to skip
            limit: Max records
            
        Returns:
            List of alert events
        """
        return self.db.query(AlertEvent).filter(
            AlertEvent.sensor_id == sensor_id
        ).order_by(desc(AlertEvent.created_at)).offset(skip).limit(limit).all()
    
    def get_unresolved(self, skip: int = 0, limit: int = 100) -> List[AlertEvent]:
        """
        Get unresolved alerts.
        
        Args:
            skip: Records to skip
            limit: Max records
            
        Returns:
            List of unresolved alerts
        """
        return self.db.query(AlertEvent).filter(
            AlertEvent.is_resolved == False
        ).order_by(desc(AlertEvent.created_at)).offset(skip).limit(limit).all()
    
    def get_by_level(
        self,
        alert_level: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[AlertEvent]:
        """
        Get alerts by level.
        
        Args:
            alert_level: Alert level (Info, Warning, Critical)
            skip: Records to skip
            limit: Max records
            
        Returns:
            List of alerts with this level
        """
        return self.db.query(AlertEvent).filter(
            AlertEvent.alert_level == alert_level
        ).order_by(desc(AlertEvent.created_at)).offset(skip).limit(limit).all()
    
    def get_critical_unresolved(self) -> List[AlertEvent]:
        """
        Get critical unresolved alerts.
        
        Returns:
            List of critical unresolved alerts
        """
        return self.db.query(AlertEvent).filter(
            and_(
                AlertEvent.alert_level == "Critical",
                AlertEvent.is_resolved == False
            )
        ).order_by(desc(AlertEvent.created_at)).all()
    
    def resolve(self, id: int) -> bool:
        """
        Mark alert as resolved.
        
        Args:
            id: Alert event ID
            
        Returns:
            True if resolved, False if not found
        """
        event = self.get_by_id(id)
        if event:
            event.is_resolved = True
            event.resolved_at = datetime.utcnow()
            self.db.commit()
            return True
        return False
    
    def count_unresolved(self) -> int:
        """
        Count unresolved alerts.
        
        Returns:
            Number of unresolved alerts
        """
        return self.db.query(AlertEvent).filter(
            AlertEvent.is_resolved == False
        ).count()
