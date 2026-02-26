"""
Machine Learning - Main Engine
Orquestra operações de machine learning: detecção de anomalias e forecasting
"""
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np

from src.ml.anomaly_detector import AnomalyDetector
from src.ml.forecaster import TimeSeriesForecaster
from src.data.database import DatabaseManager
from src.data.models import SensorReading, MLPrediction, SensorConfig
from config.settings import Config

logger = logging.getLogger(__name__)


class MLEngine:
    """
    Engine central para operações de ML.
    
    Funcionalidades:
    - Treino de modelos de anomalia e forecasting
    - Realização de predições
    - Persistência de resultados
    - Monitoramento de qualidade dos modelos
    """

    def __init__(self):
        """Inicializa o ML Engine"""
        self.anomaly_detectors = {}  # sensor_id -> AnomalyDetector
        self.forecasters = {}         # sensor_id -> TimeSeriesForecaster
        self.db = DatabaseManager(Config.DATABASE_URL)
        logger.info("✓ MLEngine inicializado")

    def get_sensor_history(
        self,
        sensor_id: int,
        hours: int = 72
    ) -> Tuple[List[datetime], List[float]]:
        """
        Recupera histórico de leituras de um sensor.
        
        Args:
            sensor_id: ID do sensor
            hours: Número de horas históricas a recuperar
            
        Returns:
            Tuple com (timestamps, values)
        """
        try:
            session = self.db.get_session()
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)

            readings = session.query(SensorReading).filter(
                SensorReading.sensor_id == sensor_id,
                SensorReading.timestamp >= cutoff_time,
                SensorReading.data_quality == 0  # Apenas dados com boa qualidade
            ).order_by(SensorReading.timestamp).all()

            if not readings:
                logger.warning(f"⚠️ Nenhuma leitura para sensor {sensor_id}")
                session.close()
                return [], []

            timestamps = [r.timestamp for r in readings]
            values = [r.value for r in readings]

            logger.info(f"✓ {len(readings)} leituras recuperadas para sensor {sensor_id}")
            session.close()
            return timestamps, values

        except Exception as e:
            logger.error(f"❌ Erro ao recuperar histórico: {e}")
            if session:
                session.close()
            return [], []

    def train_anomaly_detector(
        self,
        sensor_id: int,
        hours: int = 168,
        contamination: float = 0.1
    ) -> bool:
        """
        Treina o detector de anomalias para um sensor.
        
        Args:
            sensor_id: ID do sensor
            hours: Janela histórica para treino
            contamination: Taxa de contaminação esperada
            
        Returns:
            True se sucesso, False caso contrário
        """
        try:
            timestamps, values = self.get_sensor_history(sensor_id, hours)

            if len(values) < 30:
                logger.warning(f"⚠️ Dados insuficientes para treino: {len(values)} < 30")
                return False

            # Criar e treinar detector
            detector = AnomalyDetector(contamination=contamination)
            detector.fit(np.array(values))

            self.anomaly_detectors[sensor_id] = detector
            logger.info(f"✓ Anomaly detector treinado para sensor {sensor_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Erro ao treinar anomaly detector: {e}")
            return False

    def train_forecaster(
        self,
        sensor_id: int,
        hours: int = 72
    ) -> bool:
        """
        Treina o forecaster para um sensor.
        
        Args:
            sensor_id: ID do sensor
            hours: Janela histórica para treino
            
        Returns:
            True se sucesso, False caso contrário
        """
        try:
            timestamps, values = self.get_sensor_history(sensor_id, hours)

            if len(values) < 50:
                logger.warning(f"⚠️ Dados insuficientes para forecasting: {len(values)} < 50")
                return False

            # Criar e treinar forecaster
            forecaster = TimeSeriesForecaster(interval_width=0.95)
            forecaster.fit(timestamps, values)

            self.forecasters[sensor_id] = forecaster
            logger.info(f"✓ Forecaster treinado para sensor {sensor_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Erro ao treinar forecaster: {e}")
            return False

    def detect_anomalies(self, sensor_id: int) -> Dict:
        """
        Detecta anomalias na leitura mais recente de um sensor.
        
        Args:
            sensor_id: ID do sensor
            
        Returns:
            Dicionário com resultados da detecção
        """
        try:
            # Treinar se não está treinado
            if sensor_id not in self.anomaly_detectors:
                if not self.train_anomaly_detector(sensor_id):
                    return {'error': 'Dados insuficientes'}

            detector = self.anomaly_detectors[sensor_id]

            # Recuperar dados recentes
            timestamps, values = self.get_sensor_history(sensor_id, hours=72)

            if not values:
                return {'error': 'Sem dados'}

            # Detectar anomalias
            predictions, scores = detector.detect_ensemble(np.array(values))
            is_anomaly = predictions[-1] == -1

            result = {
                'sensor_id': sensor_id,
                'timestamp': timestamps[-1] if timestamps else datetime.utcnow(),
                'value': values[-1],
                'is_anomaly': is_anomaly,
                'anomaly_score': float(scores[-1]),
                'historical_average': float(np.mean(values)),
                'historical_std': float(np.std(values)),
                'recent_trend': 'increasing' if values[-1] > np.mean(values[-10:]) else 'decreasing'
            }

            logger.info(f"✓ Anomalias detectadas para sensor {sensor_id}: {is_anomaly}")
            return result

        except Exception as e:
            logger.error(f"❌ Erro ao detectar anomalias: {e}")
            return {'error': str(e)}

    def forecast_sensor(self, sensor_id: int, periods: int = 24) -> Dict:
        """
        Realiza forecast para um sensor.
        
        Args:
            sensor_id: ID do sensor
            periods: Número de períodos a prever
            
        Returns:
            Dicionário com previsões
        """
        try:
            # Treinar se não está treinado
            if sensor_id not in self.forecasters:
                if not self.train_forecaster(sensor_id):
                    return {'error': 'Dados insuficientes'}

            forecaster = self.forecasters[sensor_id]

            # Realizar forecast
            forecast = forecaster.forecast(periods)
            metrics = forecaster.calculate_metrics()
            summary = forecaster.forecast_summary(periods)

            result = {
                'sensor_id': sensor_id,
                'forecast': forecast,
                'metrics': metrics,
                'summary': summary,
                'timestamp': datetime.utcnow()
            }

            logger.info(f"✓ Forecast realizado para sensor {sensor_id} ({periods} períodos)")
            return result

        except Exception as e:
            logger.error(f"❌ Erro ao realizar forecast: {e}")
            return {'error': str(e)}

    def save_prediction(
        self,
        sensor_id: int,
        model_type: str,
        prediction_timestamp: datetime,
        forecasted_value: Optional[float] = None,
        confidence_low: Optional[float] = None,
        confidence_high: Optional[float] = None,
        anomaly_score: Optional[float] = None,
        is_anomaly: Optional[bool] = None
    ) -> Optional[int]:
        """
        Salva uma predição no banco de dados.
        
        Args:
            sensor_id: ID do sensor
            model_type: Tipo de modelo (FORECASTER, ANOMALY_DETECTOR)
            prediction_timestamp: Timestamp da predição
            forecasted_value: Valor previsado
            confidence_low: Limite inferior de confiança
            confidence_high: Limite superior de confiança
            anomaly_score: Score de anomalia
            is_anomaly: Se é uma anomalia
            
        Returns:
            ID da predição salva, ou None em caso de erro
        """
        try:
            session = self.db.get_session()
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

            session.add(prediction)
            session.commit()

            pred_id = prediction.prediction_id
            logger.info(f"✓ Predição salva para sensor {sensor_id} (ID: {pred_id})")
            session.close()
            return pred_id

        except Exception as e:
            logger.error(f"❌ Erro ao salvar predição: {e}")
            if session:
                session.rollback()
                session.close()
            return None

    def get_predictions(
        self,
        sensor_id: int,
        model_type: str = 'FORECASTER',
        limit: int = 100
    ) -> List[Dict]:
        """
        Recupera predições de um sensor.
        
        Args:
            sensor_id: ID do sensor
            model_type: Tipo de modelo a filtrar
            limit: Número máximo de predições a retornar
            
        Returns:
            Lista de predições
        """
        try:
            session = self.db.get_session()
            predictions = session.query(MLPrediction).filter(
                MLPrediction.sensor_id == sensor_id,
                MLPrediction.model_type == model_type
            ).order_by(MLPrediction.created_at.desc()).limit(limit).all()

            result = [
                {
                    'prediction_id': p.prediction_id,
                    'timestamp': p.prediction_timestamp,
                    'forecasted_value': p.forecasted_value,
                    'confidence_low': p.confidence_interval_low,
                    'confidence_high': p.confidence_interval_high,
                    'anomaly_score': p.anomaly_score,
                    'is_anomaly': p.is_anomaly,
                    'created_at': p.created_at
                }
                for p in predictions
            ]

            logger.info(f"✓ {len(result)} predições recuperadas para sensor {sensor_id}")
            session.close()
            return result

        except Exception as e:
            logger.error(f"❌ Erro ao recuperar predições: {e}")
            return []

    def retrain_all_models(self) -> Dict:
        """
        Retreina todos os modelos para todos os sensores.
        
        Returns:
            Dicionário com resultados do retreino
        """
        try:
            session = self.db.get_session()
            sensors = session.query(SensorConfig).filter(
                SensorConfig.enabled == True
            ).all()
            session.close()

            results = {
                'anomaly_trained': 0,
                'forecaster_trained': 0,
                'total_sensors': len(sensors),
                'timestamp': datetime.utcnow()
            }

            for sensor in sensors:
                if self.train_anomaly_detector(sensor.sensor_id):
                    results['anomaly_trained'] += 1

                if self.train_forecaster(sensor.sensor_id):
                    results['forecaster_trained'] += 1

            logger.info(f"✓ Retreino concluído: {results['anomaly_trained']} anomaly, {results['forecaster_trained']} forecaster")
            return results

        except Exception as e:
            logger.error(f"❌ Erro ao retreinar modelos: {e}")
            return {'error': str(e)}

    def get_ml_status(self) -> Dict:
        """
        Retorna status dos modelos ML.
        
        Returns:
            Dicionário com status
        """
        session = self.db.get_session()
        sensors = session.query(SensorConfig).filter(
            SensorConfig.enabled == True
        ).count()
        session.close()

        return {
            'anomaly_detectors_trained': len(self.anomaly_detectors),
            'forecasters_trained': len(self.forecasters),
            'total_sensors': sensors,
            'coverage_anomaly': f"{(len(self.anomaly_detectors) / sensors * 100):.1f}%" if sensors else "0%",
            'coverage_forecaster': f"{(len(self.forecasters) / sensors * 100):.1f}%" if sensors else "0%",
            'timestamp': datetime.utcnow()
        }

    def __del__(self):
        """Cleanup"""
        pass  # DatabaseManager handles its own cleanup


def create_ml_engine() -> MLEngine:
    """Factory para criar instância de MLEngine"""
    return MLEngine()
