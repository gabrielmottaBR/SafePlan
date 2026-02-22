"""
SQLAlchemy ORM models for SafePlan database.
Defines all data entities: sensors, readings, alerts, predictions, notifications.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class SensorConfig(Base):
    """Configuração de sensores e seus thresholds"""
    __tablename__ = 'sensor_config'

    sensor_id = Column(Integer, primary_key=True, autoincrement=True)
    internal_name = Column(String(100), unique=True, nullable=False)
    display_name = Column(String(100), nullable=False)
    sensor_type = Column(String(50), nullable=False)  # CH4_POINT, H2S, CO2, FLAME, etc.
    platform = Column(String(20), nullable=False)      # P74, P75, FPAB, etc.
    pi_server_tag = Column(String(200), nullable=True)
    unit = Column(String(20), nullable=False)

    # Novos campos do PI AF
    id_af = Column(String(100), nullable=True)         # ID único no PI AF Server
    descricao = Column(String(255), nullable=True)     # Descrição/PI Data Archive TAG
    fabricante = Column(String(100), nullable=True)    # Fabricante do sensor
    tipo_gas = Column(String(50), nullable=True)       # ch4, o2, h2s, co2, etc.
    tipo_leitura = Column(String(50), nullable=True)   # PCT, ppm, %, unidade de medida
    grupo = Column(String(100), nullable=True)         # Grupo de agrupamento
    uep = Column(String(50), nullable=True)            # Unidade/Plataforma (pode ser diferente de platform)
    valor_ma = Column(Float, nullable=True)            # Leitura em miliamper
    valor_pct = Column(Float, nullable=True)           # Leitura em percentual
    path_af = Column(String(500), nullable=True)       # Caminho completo no PI AF

    # Thresholds (configuráveis por sensor)
    lower_ok_limit = Column(Float, nullable=True)
    lower_warning_limit = Column(Float, nullable=True)
    upper_warning_limit = Column(Float, nullable=True)
    upper_critical_limit = Column(Float, nullable=True)

    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    readings = relationship('SensorReading', back_populates='sensor')
    alert_definitions = relationship('AlertDefinition', back_populates='sensor')
    alert_history = relationship('AlertHistory', back_populates='sensor')
    predictions = relationship('MLPrediction', back_populates='sensor')

    def __repr__(self):
        return f"<SensorConfig {self.internal_name} ({self.platform}) - {self.tipo_gas}>"


class SensorReading(Base):
    """Leituras de sensores (time-series)"""
    __tablename__ = 'sensor_readings'
    __table_args__ = (
        Index('idx_sensor_readings_sensor_id', 'sensor_id'),
        Index('idx_sensor_readings_timestamp', 'timestamp'),
        Index('idx_sensor_timestamp', 'sensor_id', 'timestamp'),
    )

    reading_id = Column(Integer, primary_key=True, autoincrement=True)
    sensor_id = Column(Integer, ForeignKey('sensor_config.sensor_id'), nullable=False)
    value = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    unit = Column(String(20), nullable=True)
    data_quality = Column(Integer, default=0)  # 0=good, 1=questionable, 2=bad
    fetched_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    sensor = relationship('SensorConfig', back_populates='readings')

    def __repr__(self):
        return f"<SensorReading sensor_id={self.sensor_id} value={self.value} at {self.timestamp}>"


class AlertDefinition(Base):
    """Definições de alertas (regras de triggering)"""
    __tablename__ = 'alert_definitions'

    alert_def_id = Column(Integer, primary_key=True, autoincrement=True)
    sensor_id = Column(Integer, ForeignKey('sensor_config.sensor_id'), nullable=False)
    condition_type = Column(String(50), nullable=False)  # THRESHOLD, ANOMALY, FORECAST
    severity_level = Column(Integer, nullable=False)     # 1=OK, 2=Warning, 3=Danger, 4=Critical
    threshold_value = Column(Float, nullable=True)
    anomaly_threshold = Column(Float, nullable=True)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    sensor = relationship('SensorConfig', back_populates='alert_definitions')
    alert_history = relationship('AlertHistory', back_populates='alert_definition')

    def __repr__(self):
        return f"<AlertDefinition sensor_id={self.sensor_id} severity={self.severity_level}>"


class AlertHistory(Base):
    """Histórico de alertas disparados"""
    __tablename__ = 'alert_history'
    __table_args__ = (
        Index('idx_alert_history_sensor_id', 'sensor_id'),
        Index('idx_alert_history_timestamp', 'triggered_at'),
    )

    alert_id = Column(Integer, primary_key=True, autoincrement=True)
    alert_def_id = Column(Integer, ForeignKey('alert_definitions.alert_def_id'), nullable=False)
    sensor_id = Column(Integer, ForeignKey('sensor_config.sensor_id'), nullable=False)
    triggered_at = Column(DateTime, default=datetime.utcnow)
    sensor_value = Column(Float, nullable=False)
    severity_level = Column(Integer, nullable=False)
    status = Column(String(20), default='ACTIVE')  # ACTIVE, ACKNOWLEDGED, RESOLVED
    acknowledged_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)

    # Relationships
    alert_definition = relationship('AlertDefinition', back_populates='alert_history')
    sensor = relationship('SensorConfig', back_populates='alert_history')
    notifications = relationship('NotificationLog', back_populates='alert')

    def __repr__(self):
        return f"<AlertHistory sensor_id={self.sensor_id} severity={self.severity_level} status={self.status}>"


class MLPrediction(Base):
    """Predições de ML (forecasting, anomaly scores)"""
    __tablename__ = 'ml_predictions'
    __table_args__ = (
        Index('idx_ml_predictions_sensor_id', 'sensor_id'),
    )

    prediction_id = Column(Integer, primary_key=True, autoincrement=True)
    sensor_id = Column(Integer, ForeignKey('sensor_config.sensor_id'), nullable=False)
    prediction_timestamp = Column(DateTime, nullable=False)
    model_type = Column(String(50), nullable=False)  # FORECASTER, ANOMALY_DETECTOR
    forecasted_value = Column(Float, nullable=True)
    confidence_interval_low = Column(Float, nullable=True)
    confidence_interval_high = Column(Float, nullable=True)
    anomaly_score = Column(Float, nullable=True)
    is_anomaly = Column(Boolean, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    sensor = relationship('SensorConfig', back_populates='predictions')

    def __repr__(self):
        return f"<MLPrediction sensor_id={self.sensor_id} model={self.model_type}>"


class NotificationLog(Base):
    """Log de notificações enviadas (Teams, etc.)"""
    __tablename__ = 'notification_log'

    notification_id = Column(Integer, primary_key=True, autoincrement=True)
    alert_id = Column(Integer, ForeignKey('alert_history.alert_id'), nullable=False)
    channel = Column(String(20), default='TEAMS')
    message = Column(Text, nullable=True)
    status = Column(String(20), default='PENDING')  # PENDING, SENT, FAILED
    sent_at = Column(DateTime, nullable=True)
    response_code = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)

    # Relationship
    alert = relationship('AlertHistory', back_populates='notifications')

    def __repr__(self):
        return f"<NotificationLog alert_id={self.alert_id} status={self.status}>"
