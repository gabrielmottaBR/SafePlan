"""
Data Access Objects (DAO) - Repository pattern for database operations.
Abstrai lógica de persistência e permite operações CRUD tipadas.
"""
from typing import List, Optional, Generic, TypeVar, Type
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from src.data.models import (
    SensorConfig, SensorReading, AlertDefinition, AlertHistory,
    MLPrediction, NotificationLog
)

T = TypeVar('T')


class BaseRepository(Generic[T]):
    """Base repository com operações CRUD genéricas"""

    def __init__(self, model: Type[T], session: Session):
        self.model = model
        self.session = session

    def create(self, obj: T) -> T:
        """Cria novo objeto no banco"""
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def get_by_id(self, obj_id: int) -> Optional[T]:
        """Busca objeto por ID"""
        return self.session.query(self.model).filter(
            self.model.__table__.c.keys().__iter__().__next__() == obj_id
        ).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Retorna todos os objetos com paginação"""
        return self.session.query(self.model).offset(skip).limit(limit).all()

    def update(self, obj_id: int, data: dict) -> Optional[T]:
        """Atualiza objeto por ID"""
        obj = self.get_by_id(obj_id)
        if obj:
            for key, value in data.items():
                setattr(obj, key, value)
            self.session.commit()
            self.session.refresh(obj)
        return obj

    def delete(self, obj_id: int) -> bool:
        """Deleta objeto por ID"""
        obj = self.get_by_id(obj_id)
        if obj:
            self.session.delete(obj)
            self.session.commit()
            return True
        return False

    def delete_all(self) -> int:
        """Deleta todos os objetos (CUIDADO!)"""
        count = self.session.query(self.model).delete()
        self.session.commit()
        return count


class SensorConfigRepository:
    """Repository para SensorConfig"""

    def __init__(self, session: Session):
        self.session = session

    def create(self, internal_name: str, display_name: str, sensor_type: str,
               platform: str, unit: str, pi_server_tag: str = None,
               lower_ok_limit: float = None, lower_warning_limit: float = None,
               upper_warning_limit: float = None, upper_critical_limit: float = None,
               enabled: bool = True) -> SensorConfig:
        """Cria novo sensor"""
        sensor = SensorConfig(
            internal_name=internal_name,
            display_name=display_name,
            sensor_type=sensor_type,
            platform=platform,
            unit=unit,
            pi_server_tag=pi_server_tag,
            lower_ok_limit=lower_ok_limit,
            lower_warning_limit=lower_warning_limit,
            upper_warning_limit=upper_warning_limit,
            upper_critical_limit=upper_critical_limit,
            enabled=enabled
        )
        self.session.add(sensor)
        self.session.commit()
        self.session.refresh(sensor)
        return sensor

    def get_by_id(self, sensor_id: int) -> Optional[SensorConfig]:
        """Busca sensor por ID"""
        return self.session.query(SensorConfig).filter(
            SensorConfig.sensor_id == sensor_id
        ).first()

    def get_by_name(self, internal_name: str) -> Optional[SensorConfig]:
        """Busca sensor por nome interno"""
        return self.session.query(SensorConfig).filter(
            SensorConfig.internal_name == internal_name
        ).first()

    def get_by_platform(self, platform: str) -> List[SensorConfig]:
        """Busca todos os sensores de uma plataforma"""
        return self.session.query(SensorConfig).filter(
            SensorConfig.platform == platform,
            SensorConfig.enabled == True
        ).all()

    def get_all_enabled(self) -> List[SensorConfig]:
        """Retorna todos os sensores habilitados"""
        return self.session.query(SensorConfig).filter(
            SensorConfig.enabled == True
        ).all()

    def get_all(self) -> List[SensorConfig]:
        """Retorna todos os sensores"""
        return self.session.query(SensorConfig).all()

    def update(self, sensor_id: int, **kwargs) -> Optional[SensorConfig]:
        """Atualiza sensor"""
        sensor = self.get_by_id(sensor_id)
        if sensor:
            for key, value in kwargs.items():
                if hasattr(sensor, key):
                    setattr(sensor, key, value)
            sensor.updated_at = datetime.utcnow()
            self.session.commit()
            self.session.refresh(sensor)
        return sensor

    def delete(self, sensor_id: int) -> bool:
        """Deleta sensor"""
        sensor = self.get_by_id(sensor_id)
        if sensor:
            self.session.delete(sensor)
            self.session.commit()
            return True
        return False


class SensorReadingRepository:
    """Repository para SensorReading (time-series)"""

    def __init__(self, session: Session):
        self.session = session

    def create(self, sensor_id: int, value: float, timestamp: datetime,
               unit: str = None, data_quality: int = 0) -> SensorReading:
        """Cria nova leitura de sensor"""
        reading = SensorReading(
            sensor_id=sensor_id,
            value=value,
            timestamp=timestamp,
            unit=unit,
            data_quality=data_quality
        )
        self.session.add(reading)
        self.session.commit()
        self.session.refresh(reading)
        return reading

    def get_latest(self, sensor_id: int) -> Optional[SensorReading]:
        """Retorna última leitura de um sensor"""
        return self.session.query(SensorReading).filter(
            SensorReading.sensor_id == sensor_id
        ).order_by(SensorReading.timestamp.desc()).first()

    def get_by_time_range(self, sensor_id: int, start: datetime,
                          end: datetime) -> List[SensorReading]:
        """Retorna leituras em intervalo de tempo"""
        return self.session.query(SensorReading).filter(
            and_(
                SensorReading.sensor_id == sensor_id,
                SensorReading.timestamp >= start,
                SensorReading.timestamp <= end
            )
        ).order_by(SensorReading.timestamp.asc()).all()

    def get_recent(self, sensor_id: int, limit: int = 100) -> List[SensorReading]:
        """Retorna últimas N leituras de um sensor"""
        return self.session.query(SensorReading).filter(
            SensorReading.sensor_id == sensor_id
        ).order_by(SensorReading.timestamp.desc()).limit(limit).all()

    def delete_older_than(self, before_date: datetime) -> int:
        """Delete leituras antigas (data retention policy)"""
        count = self.session.query(SensorReading).filter(
            SensorReading.timestamp < before_date
        ).delete()
        self.session.commit()
        return count


class AlertDefinitionRepository:
    """Repository para AlertDefinition"""

    def __init__(self, session: Session):
        self.session = session

    def create(self, sensor_id: int, condition_type: str, severity_level: int,
               threshold_value: float = None, anomaly_threshold: float = None,
               enabled: bool = True) -> AlertDefinition:
        """Cria nova definição de alerta"""
        alert_def = AlertDefinition(
            sensor_id=sensor_id,
            condition_type=condition_type,
            severity_level=severity_level,
            threshold_value=threshold_value,
            anomaly_threshold=anomaly_threshold,
            enabled=enabled
        )
        self.session.add(alert_def)
        self.session.commit()
        self.session.refresh(alert_def)
        return alert_def

    def get_by_sensor(self, sensor_id: int) -> List[AlertDefinition]:
        """Retorna todas as definições de alerta de um sensor"""
        return self.session.query(AlertDefinition).filter(
            AlertDefinition.sensor_id == sensor_id,
            AlertDefinition.enabled == True
        ).all()

    def get_all_enabled(self) -> List[AlertDefinition]:
        """Retorna todas as definições habilitadas"""
        return self.session.query(AlertDefinition).filter(
            AlertDefinition.enabled == True
        ).all()


class AlertHistoryRepository:
    """Repository para AlertHistory"""

    def __init__(self, session: Session):
        self.session = session

    def create(self, alert_def_id: int, sensor_id: int, sensor_value: float,
               severity_level: int) -> AlertHistory:
        """Cria novo alerta"""
        alert = AlertHistory(
            alert_def_id=alert_def_id,
            sensor_id=sensor_id,
            sensor_value=sensor_value,
            severity_level=severity_level,
            status='ACTIVE'
        )
        self.session.add(alert)
        self.session.commit()
        self.session.refresh(alert)
        return alert

    def get_active_by_sensor(self, sensor_id: int) -> List[AlertHistory]:
        """Retorna alertas ativos de um sensor"""
        return self.session.query(AlertHistory).filter(
            and_(
                AlertHistory.sensor_id == sensor_id,
                AlertHistory.status == 'ACTIVE'
            )
        ).all()

    def get_recent(self, limit: int = 100) -> List[AlertHistory]:
        """Retorna alertas recentes"""
        return self.session.query(AlertHistory).order_by(
            AlertHistory.triggered_at.desc()
        ).limit(limit).all()

    def acknowledge(self, alert_id: int) -> Optional[AlertHistory]:
        """Marca alerta como reconhecido"""
        alert = self.session.query(AlertHistory).filter(
            AlertHistory.alert_id == alert_id
        ).first()
        if alert:
            alert.status = 'ACKNOWLEDGED'
            alert.acknowledged_at = datetime.utcnow()
            self.session.commit()
            self.session.refresh(alert)
        return alert

    def resolve(self, alert_id: int) -> Optional[AlertHistory]:
        """Marca alerta como resolvido"""
        alert = self.session.query(AlertHistory).filter(
            AlertHistory.alert_id == alert_id
        ).first()
        if alert:
            alert.status = 'RESOLVED'
            alert.resolved_at = datetime.utcnow()
            self.session.commit()
            self.session.refresh(alert)
        return alert


class MLPredictionRepository:
    """Repository para MLPrediction"""

    def __init__(self, session: Session):
        self.session = session

    def create(self, sensor_id: int, prediction_timestamp: datetime,
               model_type: str, forecasted_value: float = None,
               confidence_interval_low: float = None,
               confidence_interval_high: float = None,
               anomaly_score: float = None, is_anomaly: bool = None) -> MLPrediction:
        """Cria nova predição ML"""
        prediction = MLPrediction(
            sensor_id=sensor_id,
            prediction_timestamp=prediction_timestamp,
            model_type=model_type,
            forecasted_value=forecasted_value,
            confidence_interval_low=confidence_interval_low,
            confidence_interval_high=confidence_interval_high,
            anomaly_score=anomaly_score,
            is_anomaly=is_anomaly
        )
        self.session.add(prediction)
        self.session.commit()
        self.session.refresh(prediction)
        return prediction

    def get_latest_forecast(self, sensor_id: int) -> Optional[MLPrediction]:
        """Retorna última previsão de um sensor"""
        return self.session.query(MLPrediction).filter(
            and_(
                MLPrediction.sensor_id == sensor_id,
                MLPrediction.model_type == 'FORECASTER'
            )
        ).order_by(MLPrediction.created_at.desc()).first()

    def get_latest_anomaly(self, sensor_id: int) -> Optional[MLPrediction]:
        """Retorna último score de anomalia"""
        return self.session.query(MLPrediction).filter(
            and_(
                MLPrediction.sensor_id == sensor_id,
                MLPrediction.model_type == 'ANOMALY_DETECTOR'
            )
        ).order_by(MLPrediction.created_at.desc()).first()


class NotificationLogRepository:
    """Repository para NotificationLog"""

    def __init__(self, session: Session):
        self.session = session

    def create(self, alert_id: int, channel: str = 'TEAMS',
               message: str = None, status: str = 'PENDING') -> NotificationLog:
        """Cria novo log de notificação"""
        notification = NotificationLog(
            alert_id=alert_id,
            channel=channel,
            message=message,
            status=status
        )
        self.session.add(notification)
        self.session.commit()
        self.session.refresh(notification)
        return notification

    def mark_sent(self, notification_id: int, response_code: int = 200) -> Optional[NotificationLog]:
        """Marca notificação como enviada"""
        notification = self.session.query(NotificationLog).filter(
            NotificationLog.notification_id == notification_id
        ).first()
        if notification:
            notification.status = 'SENT'
            notification.sent_at = datetime.utcnow()
            notification.response_code = response_code
            self.session.commit()
            self.session.refresh(notification)
        return notification

    def mark_failed(self, notification_id: int, error_message: str) -> Optional[NotificationLog]:
        """Marca notificação como falha"""
        notification = self.session.query(NotificationLog).filter(
            NotificationLog.notification_id == notification_id
        ).first()
        if notification:
            notification.status = 'FAILED'
            notification.error_message = error_message
            self.session.commit()
            self.session.refresh(notification)
        return notification

    def get_pending(self, limit: int = 50) -> List[NotificationLog]:
        """Retorna notificações pendentes"""
        return self.session.query(NotificationLog).filter(
            NotificationLog.status == 'PENDING'
        ).limit(limit).all()

    def get_by_alert(self, alert_id: int) -> List[NotificationLog]:
        """Retorna todas as notificações de um alerta"""
        return self.session.query(NotificationLog).filter(
            NotificationLog.alert_id == alert_id
        ).all()


class RepositoryFactory:
    """Factory para criar repositórios com sessão gerenciada"""

    def __init__(self, session: Session):
        self.session = session

    def sensor_config(self) -> SensorConfigRepository:
        return SensorConfigRepository(self.session)

    def sensor_reading(self) -> SensorReadingRepository:
        return SensorReadingRepository(self.session)

    def alert_definition(self) -> AlertDefinitionRepository:
        return AlertDefinitionRepository(self.session)

    def alert_history(self) -> AlertHistoryRepository:
        return AlertHistoryRepository(self.session)

    def ml_prediction(self) -> MLPredictionRepository:
        return MLPredictionRepository(self.session)

    def notification_log(self) -> NotificationLogRepository:
        return NotificationLogRepository(self.session)
