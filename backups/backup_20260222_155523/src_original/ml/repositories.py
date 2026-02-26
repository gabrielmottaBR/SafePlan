"""
ML Repositories - Data Access Layer for ML operations
Fornece abstrações para acesso a dados de predições e modelos
"""
import logging
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from src.data.models import MLPrediction, SensorReading, SensorConfig

logger = logging.getLogger(__name__)


class PredictionRepository:
    """Repository para operações com MLPrediction"""

    def __init__(self, session: Session):
        """
        Args:
            session: SQLAlchemy session
        """
        self.session = session

    def create(
        self,
        sensor_id: int,
        model_type: str,
        prediction_timestamp: datetime,
        forecasted_value: Optional[float] = None,
        confidence_low: Optional[float] = None,
        confidence_high: Optional[float] = None,
        anomaly_score: Optional[float] = None,
        is_anomaly: Optional[bool] = None
    ) -> Optional[MLPrediction]:
        """Cria nova predição"""
        try:
            prediction = MLPrediction(
                sensor_id=sensor_id,
                model_type=model_type,
                prediction_timestamp=prediction_timestamp,
                forecasted_value=forecasted_value,
                confidence_interval_low=confidence_low,
                confidence_interval_high=confidence_high,
                anomaly_score=anomaly_score,
                is_anomaly=is_anomaly
            )
            self.session.add(prediction)
            self.session.commit()
            logger.info(f"✓ Predição criada: sensor_id={sensor_id}, model_type={model_type}")
            return prediction
        except Exception as e:
            logger.error(f"❌ Erro ao criar predição: {e}")
            self.session.rollback()
            return None

    def find_by_sensor(
        self,
        sensor_id: int,
        model_type: Optional[str] = None,
        limit: int = 100
    ) -> List[MLPrediction]:
        """Encontra predições por sensor"""
        try:
            query = self.session.query(MLPrediction).filter(
                MLPrediction.sensor_id == sensor_id
            )

            if model_type:
                query = query.filter(MLPrediction.model_type == model_type)

            predictions = query.order_by(MLPrediction.created_at.desc()).limit(limit).all()
            logger.info(f"✓ {len(predictions)} predições encontradas para sensor {sensor_id}")
            return predictions

        except Exception as e:
            logger.error(f"❌ Erro ao buscar predições: {e}")
            return []

    def find_recent(
        self,
        sensor_id: int,
        model_type: str,
        hours: int = 24
    ) -> List[MLPrediction]:
        """Encontra predições recentes (últimas N horas)"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)

            predictions = self.session.query(MLPrediction).filter(
                MLPrediction.sensor_id == sensor_id,
                MLPrediction.model_type == model_type,
                MLPrediction.created_at >= cutoff_time
            ).order_by(MLPrediction.created_at.desc()).all()

            logger.info(f"✓ {len(predictions)} predições recentes encontradas")
            return predictions

        except Exception as e:
            logger.error(f"❌ Erro ao buscar predições recentes: {e}")
            return []

    def find_anomalies(self, sensor_id: int, limit: int = 50) -> List[MLPrediction]:
        """Encontra anomalias detectadas para um sensor"""
        try:
            predictions = self.session.query(MLPrediction).filter(
                MLPrediction.sensor_id == sensor_id,
                MLPrediction.model_type == 'ANOMALY_DETECTOR',
                MLPrediction.is_anomaly == True
            ).order_by(MLPrediction.created_at.desc()).limit(limit).all()

            logger.info(f"✓ {len(predictions)} anomalias encontradas para sensor {sensor_id}")
            return predictions

        except Exception as e:
            logger.error(f"❌ Erro ao buscar anomalias: {e}")
            return []

    def get_latest(self, sensor_id: int, model_type: str) -> Optional[MLPrediction]:
        """Obtém a predição mais recente para um sensor"""
        try:
            prediction = self.session.query(MLPrediction).filter(
                MLPrediction.sensor_id == sensor_id,
                MLPrediction.model_type == model_type
            ).order_by(MLPrediction.created_at.desc()).first()

            return prediction

        except Exception as e:
            logger.error(f"❌ Erro ao obter predição mais recente: {e}")
            return None

    def get_statistics(self, sensor_id: int) -> Dict:
        """Obtém estatísticas de predições de um sensor"""
        try:
            total_forecasts = self.session.query(MLPrediction).filter(
                MLPrediction.sensor_id == sensor_id,
                MLPrediction.model_type == 'FORECASTER'
            ).count()

            total_anomalies = self.session.query(MLPrediction).filter(
                MLPrediction.sensor_id == sensor_id,
                MLPrediction.model_type == 'ANOMALY_DETECTOR',
                MLPrediction.is_anomaly == True
            ).count()

            recent_anomalies = self.session.query(MLPrediction).filter(
                MLPrediction.sensor_id == sensor_id,
                MLPrediction.model_type == 'ANOMALY_DETECTOR',
                MLPrediction.is_anomaly == True,
                MLPrediction.created_at >= (datetime.utcnow() - timedelta(hours=24))
            ).count()

            stats = {
                'total_forecasts': total_forecasts,
                'total_anomalies': total_anomalies,
                'recent_anomalies_24h': recent_anomalies,
                'sensor_id': sensor_id
            }

            logger.info(f"✓ Estatísticas obtidas para sensor {sensor_id}")
            return stats

        except Exception as e:
            logger.error(f"❌ Erro ao obter estatísticas: {e}")
            return {}

    def delete_old(self, days: int = 30) -> int:
        """Deleta predições antigas"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(days=days)

            deleted = self.session.query(MLPrediction).filter(
                MLPrediction.created_at < cutoff_time
            ).delete()

            self.session.commit()
            logger.info(f"✓ {deleted} predições antigas deletadas")
            return deleted

        except Exception as e:
            logger.error(f"❌ Erro ao deletar predições antigas: {e}")
            self.session.rollback()
            return 0


class SensorReadingsRepository:
    """Repository para operações com SensorReading (dados históricos)"""

    def __init__(self, session: Session):
        self.session = session

    def get_recent(self, sensor_id: int, hours: int = 72) -> List[SensorReading]:
        """Obtém leituras recentes de um sensor"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)

            readings = self.session.query(SensorReading).filter(
                SensorReading.sensor_id == sensor_id,
                SensorReading.timestamp >= cutoff_time,
                SensorReading.data_quality == 0  # Apenas dados bons
            ).order_by(SensorReading.timestamp).all()

            logger.info(f"✓ {len(readings)} leituras recentes encontradas")
            return readings

        except Exception as e:
            logger.error(f"❌ Erro ao obter leituras recentes: {e}")
            return []

    def get_statistics(self, sensor_id: int, hours: int = 72) -> Dict:
        """Calcula estatísticas de leituras"""
        try:
            readings = self.get_recent(sensor_id, hours)

            if not readings:
                return {'error': 'Sem dados'}

            values = [r.value for r in readings]

            import numpy as np

            stats = {
                'total_readings': len(readings),
                'min_value': float(np.min(values)),
                'max_value': float(np.max(values)),
                'mean_value': float(np.mean(values)),
                'std_value': float(np.std(values)),
                'last_reading': readings[-1].value if readings else None,
                'last_timestamp': readings[-1].timestamp if readings else None
            }

            logger.info(f"✓ Estatísticas calculadas para sensor {sensor_id}")
            return stats

        except Exception as e:
            logger.error(f"❌ Erro ao calcular estatísticas: {e}")
            return {}


class ModelTrainingRepository:
    """Repository para tracking de treino de modelos"""

    def __init__(self, session: Session):
        self.session = session

    def get_trainable_sensors(self) -> List[SensorConfig]:
        """Retorna sensores que têm dados suficientes para treino"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=72)

            # Sensores com leituras nos últimos 72 horas
            sensors = self.session.query(SensorConfig).filter(
                SensorConfig.enabled == True
            ).all()

            # Filtrar por quantidade de dados
            trainable = []
            for sensor in sensors:
                reading_count = self.session.query(SensorReading).filter(
                    SensorReading.sensor_id == sensor.sensor_id,
                    SensorReading.timestamp >= cutoff_time,
                    SensorReading.data_quality == 0
                ).count()

                if reading_count >= 50:
                    trainable.append(sensor)

            logger.info(f"✓ {len(trainable)} sensores prontos para treino")
            return trainable

        except Exception as e:
            logger.error(f"❌ Erro ao obter sensores treináveis: {e}")
            return []


def create_prediction_repository(session: Session) -> PredictionRepository:
    """Factory para criar PredictionRepository"""
    return PredictionRepository(session)


def create_readings_repository(session: Session) -> SensorReadingsRepository:
    """Factory para criar SensorReadingsRepository"""
    return SensorReadingsRepository(session)


def create_training_repository(session: Session) -> ModelTrainingRepository:
    """Factory para criar ModelTrainingRepository"""
    return ModelTrainingRepository(session)
