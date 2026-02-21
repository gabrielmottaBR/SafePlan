"""
Tests for Machine Learning Module
Testes para anomaly detection, forecasting e ML engine
"""
import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

from src.ml.anomaly_detector import AnomalyDetector, create_anomaly_detector
from src.ml.forecaster import TimeSeriesForecaster, create_forecaster


class TestAnomalyDetector:
    """Testes para AnomalyDetector"""

    @pytest.fixture
    def detector(self):
        """Fixture que retorna um AnomalyDetector"""
        return AnomalyDetector(contamination=0.1)

    @pytest.fixture
    def sample_data(self):
        """Fixture com dados de exemplo (séries sem anomalias)"""
        normal_data = np.random.normal(loc=50, scale=5, size=200)
        # Adicionar poucas anomalias
        anomaly_indices = np.random.choice(200, 20, replace=False)
        for idx in anomaly_indices:
            normal_data[idx] = np.random.uniform(100, 150)  # Valores extremos
        return normal_data

    def test_detector_initialization(self, detector):
        """Testa inicialização do detector"""
        assert detector is not None
        assert detector.contamination == 0.1
        assert detector.is_fitted == False

    def test_detector_fit(self, detector, sample_data):
        """Testa treino do detector"""
        detector.fit(sample_data)
        assert detector.is_fitted == True

    def test_isolation_forest_detection(self, detector, sample_data):
        """Testa detecção com Isolation Forest"""
        detector.fit(sample_data)
        predictions, scores = detector.detect_isolation_forest(sample_data)

        assert len(predictions) == len(sample_data)
        assert len(scores) == len(sample_data)
        assert all(p in [-1, 1] for p in predictions)
        assert all(s > 0 for s in scores)

    def test_lof_detection(self, detector, sample_data):
        """Testa detecção com Local Outlier Factor"""
        detector.fit(sample_data)
        predictions, scores = detector.detect_lof(sample_data)

        assert len(predictions) == len(sample_data)
        assert len(scores) == len(sample_data)
        assert all(p in [-1, 1] for p in predictions)

    def test_ensemble_detection(self, detector, sample_data):
        """Testa detecção ensemble"""
        detector.fit(sample_data)
        predictions, scores = detector.detect_ensemble(sample_data, threshold=0.5)

        assert len(predictions) == len(sample_data)
        assert len(scores) == len(sample_data)
        assert all(p in [-1, 1] for p in predictions)
        assert all(0 <= s <= 1 for s in scores)

    def test_anomaly_summary(self, detector, sample_data):
        """Testa resumo de anomalias"""
        detector.fit(sample_data)
        summary = detector.get_anomaly_summary(sample_data)

        assert 'total_points' in summary
        assert 'total_anomalies' in summary
        assert 'anomaly_percentage' in summary
        assert summary['total_points'] == len(sample_data)
        assert 0 <= summary['anomaly_percentage'] <= 100

    def test_calculate_threshold(self, detector, sample_data):
        """Testa cálculo de threshold"""
        detector.fit(sample_data)
        threshold = detector.calculate_anomaly_threshold(sample_data, percentile=95)

        assert isinstance(threshold, (int, float))
        assert threshold > 0

    def test_factory_function(self):
        """Testa função factory"""
        detector = create_anomaly_detector(contamination=0.05)
        assert isinstance(detector, AnomalyDetector)
        assert detector.contamination == 0.05


class TestTimeSeriesForecaster:
    """Testes para TimeSeriesForecaster"""

    @pytest.fixture
    def forecaster(self):
        """Fixture que retorna um TimeSeriesForecaster"""
        return TimeSeriesForecaster(interval_width=0.95)

    @pytest.fixture
    def sample_timeseries(self):
        """Fixture com série temporal de exemplo"""
        dates = pd.date_range(start='2023-01-01', periods=200, freq='H')
        # Série com tendência + sazonalidade
        trend = np.linspace(0, 20, 200)
        seasonal = 5 * np.sin(np.arange(200) * 2 * np.pi / 24)
        noise = np.random.normal(0, 1, 200)
        values = 50 + trend + seasonal + noise

        return dates.tolist(), values.tolist()

    def test_forecaster_initialization(self, forecaster):
        """Testa inicialização do forecaster"""
        assert forecaster is not None
        assert forecaster.interval_width == 0.95
        assert forecaster.is_fitted == False

    def test_prepare_data(self, forecaster, sample_timeseries):
        """Testa preparação de dados"""
        timestamps, values = sample_timeseries
        df = forecaster.prepare_data(timestamps, values)

        assert len(df) == len(values)
        assert 'ds' in df.columns
        assert 'y' in df.columns

    def test_forecaster_fit(self, forecaster, sample_timeseries):
        """Testa treino do forecaster"""
        timestamps, values = sample_timeseries
        forecaster.fit(timestamps, values)

        assert forecaster.is_fitted == True
        assert forecaster.model is not None

    def test_forecast(self, forecaster, sample_timeseries):
        """Testa realização de forecast"""
        timestamps, values = sample_timeseries
        forecaster.fit(timestamps, values)

        result = forecaster.forecast(periods=24)

        assert 'timestamps' in result
        assert 'forecasted_values' in result
        assert 'lower_bound' in result
        assert 'upper_bound' in result
        assert len(result['forecasted_values']) == 24

    def test_forecast_with_history(self, forecaster, sample_timeseries):
        """Testa forecast com histórico"""
        timestamps, values = sample_timeseries
        forecaster.fit(timestamps, values)

        result = forecaster.forecast_with_history(periods=24)

        assert len(result) >= len(values)
        assert 'forecasted_value' in result.columns
        assert 'actual_value' in result.columns

    def test_calculate_metrics(self, forecaster, sample_timeseries):
        """Testa cálculo de métricas"""
        timestamps, values = sample_timeseries
        forecaster.fit(timestamps, values)

        metrics = forecaster.calculate_metrics()

        assert 'rmse' in metrics
        assert 'mae' in metrics
        assert metrics['rmse'] >= 0

    def test_forecast_summary(self, forecaster, sample_timeseries):
        """Testa resumo de forecast"""
        timestamps, values = sample_timeseries
        forecaster.fit(timestamps, values)

        summary = forecaster.forecast_summary(periods=24)

        assert 'trend_direction' in summary
        assert 'average_forecast' in summary
        assert summary['trend_direction'] in ['Crescente', 'Decrescente']

    def test_factory_function(self):
        """Testa função factory"""
        forecaster = create_forecaster(interval_width=0.90)
        assert isinstance(forecaster, TimeSeriesForecaster)
        assert forecaster.interval_width == 0.90


class TestAnomalyDetectorEdgeCases:
    """Testes de casos extremos para AnomalyDetector"""

    def test_single_value(self):
        """Testa com um único valor"""
        detector = AnomalyDetector()
        data = np.array([50.0])

        # Não deve crashar
        detector.fit(data)
        predictions, scores = detector.detect_isolation_forest(data)

        assert len(predictions) == 1

    def test_constant_values(self):
        """Testa com valores constantes"""
        detector = AnomalyDetector()
        data = np.ones(100) * 50.0

        detector.fit(data)
        predictions, scores = detector.detect_isolation_forest(data)

        assert len(predictions) == 100

    def test_all_anomalies(self):
        """Testa quando todos os valores são detectados como anomalias"""
        detector = AnomalyDetector(contamination=1.0)
        data = np.random.uniform(0, 100, 100)

        detector.fit(data)
        predictions, scores = detector.detect_ensemble(data)

        # Com contamination=1.0, todos devem ser anomalias
        assert predictions.count(-1) > 0

    def test_very_small_data(self):
        """Testa com poucos dados"""
        detector = AnomalyDetector()
        data = np.array([1, 2, 3, 4, 5])

        detector.fit(data)
        predictions, scores = detector.detect_isolation_forest(data)

        assert len(predictions) == len(data)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
