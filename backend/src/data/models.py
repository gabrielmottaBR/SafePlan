"""
SafePlan Data Models - SQLAlchemy ORM
Modelos para Sensor Configuration, Readings, e Alerts
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Float, Integer, String, Text, Boolean
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class SensorConfig(Base):
    """Configuração de sensores monitorados."""
    
    __tablename__ = "sensor_config"
    
    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(String(100), nullable=False, index=True)  # Sem UNIQUE (pode haver duplicatas)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    sensor_type = Column(String(50), nullable=False)  # O2, CH4, CO2, etc
    location = Column(String(255), nullable=False)
    unit = Column(String(20), nullable=False)  # %, ppm, °C, etc
    
    # Grupo e Modulo (from Excel)
    grupo = Column(String(50), nullable=True)  # Ex: 10S_FD
    modulo = Column(String(50), nullable=True)  # Ex: 10S
    
    # PI Server Integration
    pi_point_name = Column(String(255), nullable=True)
    pi_attribute_name = Column(String(255), nullable=True, default="Valor Atual")
    
    # Thresholds for alerting
    alert_threshold_min = Column(Float, nullable=True)
    alert_threshold_max = Column(Float, nullable=True)
    anomaly_threshold = Column(Float, nullable=True, default=0.85)
    
    # Valor atual (last reading)
    valor_pct = Column(Float, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<SensorConfig(id={self.id}, name={self.name}, type={self.sensor_type})>"


class SensorReading(Base):
    """Leituras de sensores ao longo do tempo."""
    
    __tablename__ = "sensor_reading"
    
    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(String(100), nullable=False, index=True)
    value = Column(Float, nullable=False)
    unit = Column(String(20), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Additional metadata
    source = Column(String(50), nullable=True)  # PI, Manual, Simulator, etc
    quality_code = Column(String(20), nullable=True)  # Good, Uncertain, Bad
    
    def __repr__(self):
        return f"<SensorReading(sensor_id={self.sensor_id}, value={self.value}, timestamp={self.timestamp})>"


class AlertRule(Base):
    """Regras de alerta para sensores."""
    
    __tablename__ = "alert_rule"
    
    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(String(100), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Condition: threshold_min, threshold_max, anomaly_score, forecast_deviation
    condition_type = Column(String(50), nullable=False)
    condition_value = Column(Float, nullable=False)
    
    # Action
    alert_level = Column(String(20), nullable=False)  # Info, Warning, Critical
    send_teams = Column(Boolean, default=True)
    send_email = Column(Boolean, default=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<AlertRule(id={self.id}, sensor_id={self.sensor_id}, condition={self.condition_type})>"


class AnomalyScore(Base):
    """Scores de anomalia calculados pelo ML."""
    
    __tablename__ = "anomaly_score"
    
    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(String(100), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    score = Column(Float, nullable=False)  # 0.0 - 1.0
    model_version = Column(String(50), nullable=False)
    is_anomaly = Column(Boolean, nullable=False)  # True if score > threshold
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<AnomalyScore(sensor_id={self.sensor_id}, score={self.score:.2f}, anomaly={self.is_anomaly})>"


class Forecast(Base):
    """Previsões geradas pelo ML."""
    
    __tablename__ = "forecast"
    
    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(String(100), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    forecast_value = Column(Float, nullable=False)
    forecast_confidence = Column(Float, nullable=False)  # 0.0 - 1.0
    horizon_days = Column(Integer, nullable=False)  # How many days ahead
    model_version = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Forecast(sensor_id={self.sensor_id}, value={self.forecast_value}, conf={self.forecast_confidence:.2f})>"


class AlertEvent(Base):
    """Histórico de alertas disparat os."""
    
    __tablename__ = "alert_event"
    
    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(String(100), nullable=False, index=True)
    rule_id = Column(Integer, nullable=False)  # Alert Rule ID
    alert_type = Column(String(50), nullable=False)  # THRESHOLD, ANOMALY, FORECAST
    alert_level = Column(String(20), nullable=False)  # Info, Warning, Critical
    message = Column(Text, nullable=False)
    value = Column(Float, nullable=True)
    
    # Status
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<AlertEvent(sensor_id={self.sensor_id}, level={self.alert_level}, type={self.alert_type})>"
