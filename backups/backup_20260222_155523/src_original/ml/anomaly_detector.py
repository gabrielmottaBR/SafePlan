"""
Machine Learning - Anomaly Detection
Detecta anomalias em leituras de sensores usando Isolation Forest e Local Outlier Factor
"""
import logging
from typing import List, Tuple, Optional, Dict
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)


class AnomalyDetector:
    """
    Detector de anomalias com suporte a múltiplos algoritmos.
    
    Métodos:
    - Isolation Forest: Detecção baseada em isolamento de pontos
    - Local Outlier Factor: Detecção baseada em densidade local
    """

    def __init__(self, contamination: float = 0.1):
        """
        Inicializa o detector de anomalias.
        
        Args:
            contamination: Taxa esperada de anomalias (0.0 - 1.0)
        """
        self.contamination = contamination
        self.isolation_forest = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100
        )
        self.lof = LocalOutlierFactor(
            n_neighbors=20,
            contamination=contamination
        )
        self.scaler = StandardScaler()
        self.is_fitted = False
        logger.info(f"✓ AnomalyDetector inicializado com contamination={contamination}")

    def fit(self, data: np.ndarray) -> None:
        """
        Treina os modelos com dados históricos.
        
        Args:
            data: Array 1D ou 2D com valores dos sensores
        """
        try:
            if isinstance(data, list):
                data = np.array(data)

            # Garantir 2D
            if data.ndim == 1:
                data = data.reshape(-1, 1)

            # Normalizar dados
            data_scaled = self.scaler.fit_transform(data)

            # Treinar modelos
            self.isolation_forest.fit(data_scaled)
            self.lof.fit(data_scaled)

            self.is_fitted = True
            logger.info(f"✓ AnomalyDetector treinado com {len(data)} amostras")

        except Exception as e:
            logger.error(f"❌ Erro ao treinar AnomalyDetector: {e}")
            raise

    def detect_isolation_forest(self, data: np.ndarray) -> Tuple[List[int], List[float]]:
        """
        Detecta anomalias usando Isolation Forest.
        
        Args:
            data: Array com valores a analisar
            
        Returns:
            Tuple contendo:
            - Índices dos pontos anômalos (-1) ou normais (1)
            - Scores de anomalia (quanto menor, mais anômalo)
        """
        if not self.is_fitted:
            logger.warning("⚠️ Modelo não foi treinado. Treinando com dados fornecidos...")
            self.fit(data)

        try:
            if isinstance(data, list):
                data = np.array(data)

            if data.ndim == 1:
                data = data.reshape(-1, 1)

            data_scaled = self.scaler.transform(data)

            # Predições: -1 = anomalia, 1 = normal
            predictions = self.isolation_forest.predict(data_scaled)
            scores = self.isolation_forest.score_samples(data_scaled)

            # Inverter scores para que valores maiores = mais anômalo
            anomaly_scores = -scores

            return predictions.tolist(), anomaly_scores.tolist()

        except Exception as e:
            logger.error(f"❌ Erro na detecção (Isolation Forest): {e}")
            raise

    def detect_lof(self, data: np.ndarray) -> Tuple[List[int], List[float]]:
        """
        Detecta anomalias usando Local Outlier Factor.
        
        Args:
            data: Array com valores a analisar
            
        Returns:
            Tuple contendo:
            - Índices dos pontos anômalos (-1) ou normais (1)
            - Scores LOF (quanto maior, mais anômalo)
        """
        if not self.is_fitted:
            logger.warning("⚠️ Modelo não foi treinado. Treinando com dados fornecidos...")
            self.fit(data)

        try:
            if isinstance(data, list):
                data = np.array(data)

            if data.ndim == 1:
                data = data.reshape(-1, 1)

            data_scaled = self.scaler.transform(data)

            # Predições: -1 = anomalia, 1 = normal
            predictions = self.lof.fit_predict(data_scaled)
            scores = self.lof.negative_outlier_factor_

            return predictions.tolist(), scores.tolist()

        except Exception as e:
            logger.error(f"❌ Erro na detecção (LOF): {e}")
            raise

    def detect_ensemble(self, data: np.ndarray, threshold: float = 0.5) -> Tuple[List[int], List[float]]:
        """
        Detecta anomalias usando ensemble de múltiplos algoritmos.
        
        Args:
            data: Array com valores a analisar
            threshold: Threshold para votação de anomalias (0.0-1.0)
            
        Returns:
            Tuple contendo:
            - Predições ensemble (-1 = anomalia, 1 = normal)
            - Scores de confiança da anomalia
        """
        try:
            if_pred, if_scores = self.detect_isolation_forest(data)
            lof_pred, lof_scores = self.detect_lof(data)

            # Normalizar scores para 0-1
            if_scores_norm = [(s - min(if_scores)) / (max(if_scores) - min(if_scores) + 1e-8)
                               for s in if_scores]
            lof_scores_norm = [(s - min(lof_scores)) / (max(lof_scores) - min(lof_scores) + 1e-8)
                                for s in lof_scores]

            # Média dos scores normalizados
            ensemble_scores = [(if_scores_norm[i] + lof_scores_norm[i]) / 2
                               for i in range(len(if_scores_norm))]

            # Predições baseadas no threshold
            ensemble_pred = [-1 if score >= threshold else 1 for score in ensemble_scores]

            logger.info(f"✓ Ensemble detection concluído: {ensemble_pred.count(-1)} anomalias detectadas")

            return ensemble_pred, ensemble_scores

        except Exception as e:
            logger.error(f"❌ Erro na detecção ensemble: {e}")
            raise

    def calculate_anomaly_threshold(self, data: np.ndarray, percentile: float = 95) -> float:
        """
        Calcula um threshold de anomalia baseado em percentil dos dados históricos.
        
        Args:
            data: Array com valores históricos
            percentile: Percentil para calcular threshold (padrão: 95%)
            
        Returns:
            Valor do threshold
        """
        try:
            _, scores = self.detect_isolation_forest(data)
            threshold = np.percentile(scores, percentile)
            logger.info(f"✓ Threshold de anomalia calculado: {threshold:.4f} (percentil {percentile})")
            return threshold

        except Exception as e:
            logger.error(f"❌ Erro ao calcular threshold: {e}")
            raise

    def get_anomaly_summary(self, data: np.ndarray) -> Dict:
        """
        Retorna um resumo da análise de anomalias.
        
        Args:
            data: Array com valores a analisar
            
        Returns:
            Dicionário com estatísticas de anomalia
        """
        try:
            predictions, scores = self.detect_ensemble(data)

            summary = {
                'total_points': len(data),
                'total_anomalies': predictions.count(-1),
                'anomaly_percentage': (predictions.count(-1) / len(data) * 100) if data else 0,
                'avg_anomaly_score': np.mean(scores),
                'max_anomaly_score': np.max(scores),
                'min_anomaly_score': np.min(scores),
                'std_anomaly_score': np.std(scores),
                'predictions': predictions,
                'scores': scores
            }

            logger.info(f"✓ Resumo de anomalias: {summary['total_anomalies']} de {summary['total_points']} ({summary['anomaly_percentage']:.1f}%)")

            return summary

        except Exception as e:
            logger.error(f"❌ Erro ao gerar resumo de anomalias: {e}")
            raise


def create_anomaly_detector(contamination: float = 0.1) -> AnomalyDetector:
    """Factory para criar instância de AnomalyDetector"""
    return AnomalyDetector(contamination=contamination)
