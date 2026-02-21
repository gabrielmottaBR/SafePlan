"""
Machine Learning - Time Series Forecasting
Realiza previsões de valores futuros de sensores usando Prophet
"""
import logging
from typing import List, Dict, Tuple, Optional
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from prophet import Prophet

logger = logging.getLogger(__name__)


class TimeSeriesForecaster:
    """
    Forecaster de séries temporais usando Facebook Prophet.
    
    Características:
    - Detecção automática de tendências e sazonalidade
    - Intervalos de confiança ajustáveis
    - Suporte a múltiplos horizontes de previsão
    - Métricas de qualidade do modelo (MAPE, RMSE)
    """

    def __init__(
        self,
        interval_width: float = 0.95,
        yearly_seasonality: bool = True,
        weekly_seasonality: bool = True,
        daily_seasonality: bool = False
    ):
        """
        Inicializa o forecaster.
        
        Args:
            interval_width: Largura do intervalo de confiança (default: 0.95)
            yearly_seasonality: Ativar sazonalidade anual
            weekly_seasonality: Ativar sazonalidade semanal
            daily_seasonality: Ativar sazonalidade diária
        """
        self.interval_width = interval_width
        self.yearly_seasonality = yearly_seasonality
        self.weekly_seasonality = weekly_seasonality
        self.daily_seasonality = daily_seasonality
        self.model = None
        self.is_fitted = False
        self.training_data = None
        logger.info("✓ TimeSeriesForecaster inicializado")

    def prepare_data(self, timestamps: List, values: List) -> pd.DataFrame:
        """
        Prepara dados no formato esperado pelo Prophet.
        
        Args:
            timestamps: Lista de timestamps
            values: Lista de valores correspondentes
            
        Returns:
            DataFrame com colunas 'ds' (timestamp) e 'y' (valor)
        """
        try:
            df = pd.DataFrame({
                'ds': pd.to_datetime(timestamps),
                'y': values
            })

            # Ordenar por timestamp
            df = df.sort_values('ds').reset_index(drop=True)

            # Remover duplicatas mantendo a primeira
            df = df.drop_duplicates(subset=['ds'], keep='first')

            logger.info(f"✓ Dados preparados: {len(df)} registros")
            return df

        except Exception as e:
            logger.error(f"❌ Erro ao preparar dados: {e}")
            raise

    def fit(self, timestamps: List, values: List) -> None:
        """
        Treina o modelo Prophet com dados históricos.
        
        Args:
            timestamps: Lista de timestamps
            values: Lista de valores
        """
        try:
            # Preparar dados
            self.training_data = self.prepare_data(timestamps, values)

            # Criar e configurar modelo
            self.model = Prophet(
                interval_width=self.interval_width,
                yearly_seasonality=self.yearly_seasonality,
                weekly_seasonality=self.weekly_seasonality,
                daily_seasonality=self.daily_seasonality,
                changepoint_prior_scale=0.05
            )

            # Treinar
            with logging.getLogger('prophet').disabled:  # Suprimir logs do Prophet
                self.model.fit(self.training_data)

            self.is_fitted = True
            logger.info(f"✓ Modelo Prophet treinado com {len(self.training_data)} amostras")

        except Exception as e:
            logger.error(f"❌ Erro ao treinar modelo: {e}")
            raise

    def forecast(self, periods: int) -> Dict:
        """
        Realiza previsão para um número específico de períodos.
        
        Args:
            periods: Número de períodos a prever
            
        Returns:
            Dicionário contendo:
            - timestamps: Timestamps previstos
            - forecasted_values: Valores previstos
            - lower_bound: Limite inferior do intervalo de confiança
            - upper_bound: Limite superior do intervalo de confiança
            - trend: Valores de tendência
        """
        if not self.is_fitted:
            logger.error("❌ Modelo não foi treinado")
            raise ValueError("Modelo não foi treinado. Execute fit() antes.")

        try:
            # Criar dataframe de períodos futuros
            future = self.model.make_future_dataframe(periods=periods, freq='H')
            future = future[future['ds'] > self.training_data['ds'].max()]

            # Realizar previsão
            with logging.getLogger('prophet').disabled:
                forecast = self.model.predict(future)

            # Extrair resultados
            forecast_data = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper', 'trend']].copy()
            forecast_data = forecast_data[forecast_data['ds'].isin(future['ds'])]

            result = {
                'timestamps': forecast_data['ds'].dt.to_pydatetime().tolist(),
                'forecasted_values': forecast_data['yhat'].values.tolist(),
                'lower_bound': forecast_data['yhat_lower'].values.tolist(),
                'upper_bound': forecast_data['yhat_upper'].values.tolist(),
                'trend': forecast_data['trend'].values.tolist()
            }

            logger.info(f"✓ Previsão realizada para {periods} períodos")
            return result

        except Exception as e:
            logger.error(f"❌ Erro ao realizar previsão: {e}")
            raise

    def forecast_with_history(self, periods: int = 24) -> pd.DataFrame:
        """
        Retorna previsão incluindo dados históricos para visualização.
        
        Args:
            periods: Número de períodos a prever
            
        Returns:
            DataFrame com histórico + previsão
        """
        if not self.is_fitted:
            raise ValueError("Modelo não foi treinado")

        try:
            # Previsão
            future = self.model.make_future_dataframe(periods=periods, freq='H')

            with logging.getLogger('prophet').disabled:
                forecast = self.model.predict(future)

            # Combinar com treino
            result = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper', 'trend']].copy()
            result.columns = ['timestamp', 'forecasted_value', 'lower_bound', 'upper_bound', 'trend']

            # Adicionar valores reais do treino
            result['actual_value'] = None
            for idx, row in self.training_data.iterrows():
                mask = result['timestamp'] == row['ds']
                if mask.any():
                    result.loc[mask, 'actual_value'] = row['y']

            return result

        except Exception as e:
            logger.error(f"❌ Erro ao gerar previsão com histórico: {e}")
            raise

    def calculate_metrics(self) -> Dict:
        """
        Calcula métricas de qualidade do modelo baseadas em validação cruzada.
        
        Returns:
            Dicionário com métricas: MAPE, RMSE, etc.
        """
        if not self.is_fitted or len(self.training_data) < 30:
            logger.warning("⚠️ Dados insuficientes para validação cruzada")
            return {'mape': None, 'rmse': None}

        try:
            # Validação cruzada (últimos 10% dos dados)
            split_point = int(len(self.training_data) * 0.9)
            train_data = self.training_data[:split_point]
            test_data = self.training_data[split_point:]

            # Retreinar com dados de treino
            model = Prophet(
                interval_width=self.interval_width,
                yearly_seasonality=self.yearly_seasonality,
                weekly_seasonality=self.weekly_seasonality,
                daily_seasonality=self.daily_seasonality
            )

            with logging.getLogger('prophet').disabled:
                model.fit(train_data)
                forecast = model.predict(test_data[['ds']])

            # Calcular métricas
            y_true = test_data['y'].values
            y_pred = forecast['yhat'].values

            mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100 if np.any(y_true != 0) else None
            rmse = np.sqrt(np.mean((y_true - y_pred) ** 2))
            mae = np.mean(np.abs(y_true - y_pred))

            metrics = {
                'mape': mape,
                'rmse': rmse,
                'mae': mae,
                'training_samples': len(train_data),
                'test_samples': len(test_data)
            }

            logger.info(f"✓ Métricas calculadas: RMSE={rmse:.4f}, MAE={mae:.4f}, MAPE={mape:.2f}%")
            return metrics

        except Exception as e:
            logger.error(f"❌ Erro ao calcular métricas: {e}")
            return {'mape': None, 'rmse': None}

    def get_components(self) -> Dict:
        """
        Retorna componentes da previsão (tendência, sazonalidade, etc).
        
        Returns:
            Dicionário com nomes dos componentes disponíveis
        """
        if not self.is_fitted:
            raise ValueError("Modelo não foi treinado")

        try:
            components = self.model.component_modes.keys()
            logger.info(f"✓ Componentes disponíveis: {', '.join(components)}")
            return {'components': list(components)}

        except Exception as e:
            logger.error(f"❌ Erro ao obter componentes: {e}")
            raise

    def forecast_summary(self, periods: int = 24) -> Dict:
        """
        Retorna um resumo da previsão.
        
        Args:
            periods: Número de períodos a prever
            
        Returns:
            Dicionário com resumo da previsão
        """
        try:
            forecast = self.forecast(periods)
            metrics = self.calculate_metrics()

            last_value = self.training_data['y'].iloc[-1]
            avg_forecast = np.mean(forecast['forecasted_values'])
            trend_direction = 'Crescente' if avg_forecast > last_value else 'Decrescente'

            summary = {
                'periods': periods,
                'last_historical_value': float(last_value),
                'average_forecast': float(avg_forecast),
                'trend_direction': trend_direction,
                'confidence_interval': self.interval_width,
                'metrics': metrics,
                'min_forecast': float(np.min(forecast['forecasted_values'])),
                'max_forecast': float(np.max(forecast['forecasted_values'])),
                'volatility': float(np.std(forecast['forecasted_values']))
            }

            logger.info(f"✓ Resumo da previsão gerado: tendência {trend_direction}")
            return summary

        except Exception as e:
            logger.error(f"❌ Erro ao gerar resumo: {e}")
            raise


def create_forecaster(
    interval_width: float = 0.95,
    yearly_seasonality: bool = True,
    weekly_seasonality: bool = True,
    daily_seasonality: bool = False
) -> TimeSeriesForecaster:
    """Factory para criar instância de TimeSeriesForecaster"""
    return TimeSeriesForecaster(
        interval_width=interval_width,
        yearly_seasonality=yearly_seasonality,
        weekly_seasonality=weekly_seasonality,
        daily_seasonality=daily_seasonality
    )
