"""
Data fetcher para buscar dados do PI Server e persistir no banco de dados.
Responsável pelo pipeline de ingestão de dados.
"""
import logging
from datetime import datetime, timedelta
from typing import List, Optional
import pandas as pd

from config.settings import Config
from src.data.database import get_db_manager
from src.data.repositories import RepositoryFactory
from src.pi_server.pi_client import PIServerClient, get_pi_client

logger = logging.getLogger(__name__)


class DataFetcher:
    """
    Busca dados do PI Server e persiste no banco de dados SQLite.
    """

    def __init__(self, pi_client: Optional[PIServerClient] = None):
        """
        Inicializa DataFetcher.

        Args:
            pi_client: PIServerClient instance (opcional, usa global se None)
        """
        self.pi_client = pi_client or get_pi_client()
        self.db_manager = None

    def fetch_latest_readings(self, sensors: List[tuple]) -> int:
        """
        Busca últimas leituras de sensores do PI Server e persiste no banco.

        Args:
            sensors: Lista de tuplas (sensor_id, internal_name, pi_server_tag, unit)

        Returns:
            Número de leituras inseridas com sucesso
        """
        try:
            if not self.pi_client.is_connected():
                logger.warning("PI Server não conectado, tentando reconectar...")
                if not self.pi_client.connect():
                    logger.error("Falha ao reconectar ao PI Server")
                    return 0

            session = get_db_manager().get_session()
            repos = RepositoryFactory(session)
            reading_repo = repos.sensor_reading()

            inserted_count = 0
            failed_count = 0

            # Get last reading timestamp from database
            now = datetime.utcnow()
            start_time = now - timedelta(hours=1)  # Busca último 1 hora

            for sensor_id, internal_name, pi_tag, unit in sensors:
                try:
                    if not pi_tag:
                        logger.debug(f"Tag PI não configurada para {internal_name}, pulando...")
                        continue

                    logger.debug(f"Buscando dados para {internal_name} ({pi_tag})...")

                    # Fetch interpolated data (1 minute interval = latest value)
                    df = self.pi_client.get_interpolated_data(
                        tag=pi_tag,
                        start_date=start_time,
                        end_date=now,
                        interval='1m',
                        numeric_only=False
                    )

                    if df is None or df.empty:
                        logger.warning(f"Nenhum dado retornado para {pi_tag}")
                        failed_count += 1
                        continue

                    # Process and insert latest readings
                    # Keep only last 5 minutes of data to avoid duplicates
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                    df = df.sort_values('timestamp').tail(5)

                    for idx, row in df.iterrows():
                        try:
                            # Parse timestamp and value
                            timestamp = row['timestamp']
                            raw_value = row[pi_tag]

                            # Convert to float
                            try:
                                value = float(raw_value)
                            except (ValueError, TypeError):
                                logger.warning(f"Valor inválido para {pi_tag}: {raw_value}")
                                continue

                            # Check for outliers (basic validation)
                            if not self._is_valid_value(value):
                                logger.warning(f"Valor de outlier para {pi_tag}: {value}")
                                continue

                            # Insert into database
                            reading = reading_repo.create(
                                sensor_id=sensor_id,
                                value=value,
                                timestamp=timestamp,
                                unit=unit,
                                data_quality=0
                            )

                            inserted_count += 1
                            logger.debug(f"  ✓ Inserido: {value} {unit} em {timestamp}")

                        except Exception as e:
                            logger.error(f"Erro ao processar leitura de {pi_tag}: {e}")
                            failed_count += 1
                            continue

                except Exception as e:
                    logger.error(f"Erro ao buscar dados para {internal_name}: {e}")
                    failed_count += 1
                    continue

            session.close()

            logger.info(
                f"Fetch completo: {inserted_count} inseridos, "
                f"{failed_count} falhas de {len(sensors)} sensores"
            )

            return inserted_count

        except Exception as e:
            logger.error(f"Erro crítico em fetch_latest_readings: {e}")
            return 0

    def fetch_historical_data(self, sensor_id: int, pi_tag: str, days_back: int = 30) -> int:
        """
        Busca dados históricos de um sensor e persiste no banco.
        Útil para treinamento de ML models.

        Args:
            sensor_id: ID do sensor no banco
            pi_tag: Tag no PI Server
            days_back: Quantos dias de histórico buscar

        Returns:
            Número de leituras inseridas
        """
        try:
            if not self.pi_client.is_connected():
                if not self.pi_client.connect():
                    logger.error("Falha ao conectar ao PI Server")
                    return 0

            session = get_db_manager().get_session()
            repos = RepositoryFactory(session)
            reading_repo = repos.sensor_reading()

            now = datetime.utcnow()
            start_time = now - timedelta(days=days_back)

            logger.info(f"Buscando histórico de {pi_tag} dos últimos {days_back} dias...")

            # Fetch with 10-minute interval for efficiency
            df = self.pi_client.get_interpolated_data(
                tag=pi_tag,
                start_date=start_time,
                end_date=now,
                interval='10m',
                numeric_only=False
            )

            if df is None or df.empty:
                logger.warning(f"Nenhum dado histórico para {pi_tag}")
                session.close()
                return 0

            inserted_count = 0

            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp')

            for idx, row in df.iterrows():
                try:
                    timestamp = row['timestamp']
                    raw_value = row[pi_tag]

                    try:
                        value = float(raw_value)
                    except (ValueError, TypeError):
                        continue

                    if not self._is_valid_value(value):
                        continue

                    # Check if reading already exists (avoid duplicates)
                    existing = session.query(
                        'SELECT 1 FROM sensor_readings WHERE sensor_id=? AND timestamp=?',
                        (sensor_id, timestamp)
                    )
                    if existing:
                        continue

                    reading = reading_repo.create(
                        sensor_id=sensor_id,
                        value=value,
                        timestamp=timestamp,
                        unit=None,
                        data_quality=0
                    )

                    inserted_count += 1

                except Exception as e:
                    logger.debug(f"Erro ao processar leitura histórica: {e}")
                    continue

            session.close()

            logger.info(f"✓ Histórico de {pi_tag}: {inserted_count} registros inseridos")
            return inserted_count

        except Exception as e:
            logger.error(f"Erro ao buscar histórico para {pi_tag}: {e}")
            return 0

    def _is_valid_value(self, value: float) -> bool:
        """
        Valida se o valor é plausível (não é outlier óbvio).

        Args:
            value: Valor do sensor

        Returns:
            True se valor parece válido
        """
        # Basic validation: não é NaN, inf, ou número muito grande
        if pd.isna(value) or pd.isnull(value):
            return False

        if not isinstance(value, (int, float)):
            return False

        # Check for inf
        try:
            if float(value) == float('inf') or float(value) == float('-inf'):
                return False
        except (ValueError, OverflowError):
            return False

        return True

    def get_sensor_list(self) -> List[tuple]:
        """
        Retorna lista de sensores habilitados para fetch.

        Returns:
            Lista de tuplas (sensor_id, internal_name, pi_server_tag, unit)
        """
        try:
            session = get_db_manager().get_session()
            repos = RepositoryFactory(session)
            sensor_repo = repos.sensor_config()

            sensors = sensor_repo.get_all_enabled()
            sensor_list = [
                (s.sensor_id, s.internal_name, s.pi_server_tag, s.unit)
                for s in sensors if s.pi_server_tag
            ]

            session.close()
            return sensor_list

        except Exception as e:
            logger.error(f"Erro ao obter lista de sensores: {e}")
            return []


def create_data_fetcher() -> DataFetcher:
    """Factory para criar instância de DataFetcher"""
    return DataFetcher()
