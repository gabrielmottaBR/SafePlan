"""
Sensor Manager - Gerencia configuração e ciclo de vida de sensores.
Responsável por CRUD de sensores e suas definições de alerta.
"""
import logging
from typing import List, Optional, Dict

from src.data.database import get_db_manager
from src.data.repositories import RepositoryFactory
from src.data.models import SensorConfig, AlertDefinition

logger = logging.getLogger(__name__)


class SensorManager:
    """
    Gerencia sensores e suas configurações.
    """

    def __init__(self):
        """Inicializa SensorManager"""
        self.db_manager = get_db_manager()

    def create_sensor(self, internal_name: str, display_name: str, sensor_type: str,
                     platform: str, unit: str, pi_server_tag: str = None,
                     lower_ok_limit: float = None, lower_warning_limit: float = None,
                     upper_warning_limit: float = None, upper_critical_limit: float = None,
                     id_af: str = None, descricao: str = None, fabricante: str = None,
                     tipo_gas: str = None, tipo_leitura: str = None, grupo: str = None,
                     modulo: str = None, uep: str = None, valor_ma: float = None, valor_pct: float = None,
                     path_af: str = None) -> Optional[SensorConfig]:
        """
        Cria novo sensor com dados do PI AF Server.

        Args:
            internal_name: Nome interno único
            display_name: Nome para exibição
            sensor_type: Tipo do sensor
            platform: Plataforma (P74, P75, etc)
            unit: Unidade de medida
            pi_server_tag: Tag no PI Server
            lower_ok_limit: Limite inferior OK
            lower_warning_limit: Limite inferior Warning
            upper_warning_limit: Limite superior Warning
            upper_critical_limit: Limite superior Critical
            id_af: ID único no PI AF (será usado como TAG)
            descricao: Descrição do sensor
            fabricante: Fabricante
            tipo_gas: Tipo de gás (ch4, o2, h2s, etc)
            tipo_leitura: Tipo de leitura (PCT, ppm, etc)
            grupo: Grupo de agrupamento
            modulo: Módulo ao qual o sensor pertence
            uep: Unidade/Plataforma adicional
            valor_ma: Leitura em miliamper
            valor_pct: Leitura em percentual
            path_af: Caminho completo no PI AF

        Returns:
            SensorConfig criado ou None se erro
        """
        session = self.db_manager.get_session()

        try:
            repos = RepositoryFactory(session)
            sensor_repo = repos.sensor_config()

            # Check if sensor already exists
            existing = sensor_repo.get_by_name(internal_name)
            if existing:
                logger.warning(f"Sensor {internal_name} já existe")
                # Extract sensor ID before closing session
                sensor_id = existing.sensor_id
                
                # Cria wrapper para evitar session binding issues
                class SensorResult:
                    def __init__(self, sensor_id, internal_name, display_name, sensor_type):
                        self.sensor_id = sensor_id
                        self.internal_name = internal_name
                        self.display_name = display_name
                        self.sensor_type = sensor_type
                
                return SensorResult(sensor_id, existing.internal_name, existing.display_name, existing.sensor_type)

            # Create new sensor
            sensor = sensor_repo.create(
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
                id_af=id_af,
                descricao=descricao,
                fabricante=fabricante,
                tipo_gas=tipo_gas,
                tipo_leitura=tipo_leitura,
                grupo=grupo,
                modulo=modulo,
                uep=uep,
                valor_ma=valor_ma,
                valor_pct=valor_pct,
                path_af=path_af
            )

            # Flush to get sensor_id generated
            session.flush()
            sensor_id = sensor.sensor_id

            session.commit()
            logger.info(f"✓ Sensor criado: {internal_name}")
            
            # Retorna objeto com sensor_id preservado (mesmo após session.close())
            # Criamos um wrapper simples para evitar session binding issues
            class SensorResult:
                def __init__(self, obj):
                    self.sensor_id = obj.sensor_id
                    self.internal_name = obj.internal_name
                    self.display_name = obj.display_name
                    self.sensor_type = obj.sensor_type
            
            return SensorResult(sensor)

        except Exception as e:
            logger.error(f"Erro ao criar sensor: {e}")
            session.rollback()
            return None
        finally:
            session.close()

    def update_sensor(self, sensor_id: int, **kwargs) -> Optional[SensorConfig]:
        """
        Atualiza configuração de sensor.

        Args:
            sensor_id: ID do sensor
            **kwargs: Campos a atualizar

        Returns:
            SensorConfig atualizado ou None se erro
        """
        session = self.db_manager.get_session()

        try:
            repos = RepositoryFactory(session)
            sensor_repo = repos.sensor_config()

            sensor = sensor_repo.update(sensor_id, **kwargs)
            session.commit()

            logger.info(f"✓ Sensor {sensor_id} atualizado")
            return sensor

        except Exception as e:
            logger.error(f"Erro ao atualizar sensor: {e}")
            session.rollback()
            return None
        finally:
            session.close()

    def get_sensor(self, sensor_id: int) -> Optional[SensorConfig]:
        """
        Retorna sensor por ID.

        Args:
            sensor_id: ID do sensor

        Returns:
            SensorConfig ou None se não encontrado
        """
        session = self.db_manager.get_session()

        try:
            repos = RepositoryFactory(session)
            sensor_repo = repos.sensor_config()
            return sensor_repo.get_by_id(sensor_id)

        except Exception as e:
            logger.error(f"Erro ao buscar sensor: {e}")
            return None
        finally:
            session.close()

    def get_all_sensors(self) -> List[SensorConfig]:
        """
        Retorna todos os sensores.

        Returns:
            Lista de SensorConfig
        """
        session = self.db_manager.get_session()

        try:
            repos = RepositoryFactory(session)
            sensor_repo = repos.sensor_config()
            return sensor_repo.get_all()

        except Exception as e:
            logger.error(f"Erro ao buscar sensores: {e}")
            return []
        finally:
            session.close()

    def get_enabled_sensors(self) -> List[SensorConfig]:
        """
        Retorna sensores habilitados.

        Returns:
            Lista de SensorConfig habilitados
        """
        session = self.db_manager.get_session()

        try:
            repos = RepositoryFactory(session)
            sensor_repo = repos.sensor_config()
            return sensor_repo.get_all_enabled()

        except Exception as e:
            logger.error(f"Erro ao buscar sensores habilitados: {e}")
            return []
        finally:
            session.close()

    def get_platform_sensors(self, platform: str) -> List[SensorConfig]:
        """
        Retorna sensores de uma plataforma.

        Args:
            platform: Nome da plataforma

        Returns:
            Lista de SensorConfig
        """
        session = self.db_manager.get_session()

        try:
            repos = RepositoryFactory(session)
            sensor_repo = repos.sensor_config()
            return sensor_repo.get_by_platform(platform)

        except Exception as e:
            logger.error(f"Erro ao buscar sensores da plataforma {platform}: {e}")
            return []
        finally:
            session.close()

    def disable_sensor(self, sensor_id: int) -> Optional[SensorConfig]:
        """
        Disabilita sensor (soft delete).

        Args:
            sensor_id: ID do sensor

        Returns:
            SensorConfig atualizado ou None se erro
        """
        return self.update_sensor(sensor_id, enabled=False)

    def enable_sensor(self, sensor_id: int) -> Optional[SensorConfig]:
        """
        Habilita sensor.

        Args:
            sensor_id: ID do sensor

        Returns:
            SensorConfig atualizado ou None se erro
        """
        return self.update_sensor(sensor_id, enabled=True)

    def delete_sensor(self, sensor_id: int) -> bool:
        """
        Deleta sensor (hard delete).

        Args:
            sensor_id: ID do sensor

        Returns:
            True se sucesso, False se erro
        """
        session = self.db_manager.get_session()

        try:
            repos = RepositoryFactory(session)
            sensor_repo = repos.sensor_config()
            success = sensor_repo.delete(sensor_id)

            if success:
                session.commit()
                logger.info(f"✓ Sensor {sensor_id} deletado")
            else:
                session.rollback()

            return success

        except Exception as e:
            logger.error(f"Erro ao deletar sensor: {e}")
            session.rollback()
            return False
        finally:
            session.close()

    def create_alert_rule(self, sensor_id: int, condition_type: str, severity_level: int,
                         threshold_value: float = None,
                         anomaly_threshold: float = None) -> Optional[AlertDefinition]:
        """
        Cria regra de alerta para um sensor.

        Args:
            sensor_id: ID do sensor
            condition_type: Tipo de condição (THRESHOLD, ANOMALY, FORECAST)
            severity_level: Nível de severidade (1-4)
            threshold_value: Valor de threshold
            anomaly_threshold: Threshold de anomalia

        Returns:
            AlertDefinition criado ou None se erro
        """
        session = self.db_manager.get_session()

        try:
            repos = RepositoryFactory(session)
            alert_def_repo = repos.alert_definition()

            alert_def = alert_def_repo.create(
                sensor_id=sensor_id,
                condition_type=condition_type,
                severity_level=severity_level,
                threshold_value=threshold_value,
                anomaly_threshold=anomaly_threshold
            )

            session.commit()
            logger.info(f"✓ Regra de alerta criada para sensor {sensor_id}")
            return alert_def

        except Exception as e:
            logger.error(f"Erro ao criar regra de alerta: {e}")
            session.rollback()
            return None
        finally:
            session.close()

    def get_alert_rules(self, sensor_id: int) -> List[AlertDefinition]:
        """
        Retorna regras de alerta de um sensor.

        Args:
            sensor_id: ID do sensor

        Returns:
            Lista de AlertDefinition
        """
        session = self.db_manager.get_session()

        try:
            repos = RepositoryFactory(session)
            alert_def_repo = repos.alert_definition()
            return alert_def_repo.get_by_sensor(sensor_id)

        except Exception as e:
            logger.error(f"Erro ao buscar regras de alerta: {e}")
            return []
        finally:
            session.close()

    def get_sensor_status(self, sensor_id: int) -> Dict:
        """
        Retorna status completo de um sensor.

        Args:
            sensor_id: ID do sensor

        Returns:
            Dict com informações do sensor
        """
        session = self.db_manager.get_session()

        try:
            repos = RepositoryFactory(session)
            sensor_repo = repos.sensor_config()
            reading_repo = repos.sensor_reading()

            sensor = sensor_repo.get_by_id(sensor_id)

            if not sensor:
                return {}

            latest_reading = reading_repo.get_latest(sensor_id)

            status = {
                'sensor_id': sensor.sensor_id,
                'internal_name': sensor.internal_name,
                'display_name': sensor.display_name,
                'sensor_type': sensor.sensor_type,
                'platform': sensor.platform,
                'unit': sensor.unit,
                'enabled': sensor.enabled,
                'latest_value': latest_reading.value if latest_reading else None,
                'latest_timestamp': latest_reading.timestamp if latest_reading else None,
                'thresholds': {
                    'lower_ok_limit': sensor.lower_ok_limit,
                    'lower_warning_limit': sensor.lower_warning_limit,
                    'upper_warning_limit': sensor.upper_warning_limit,
                    'upper_critical_limit': sensor.upper_critical_limit
                }
            }

            return status

        except Exception as e:
            logger.error(f"Erro ao obter status do sensor: {e}")
            return {}
        finally:
            session.close()

    def get_platforms(self) -> List[str]:
        """
        Retorna lista de todas as plataformas com sensores.

        Returns:
            Lista de nomes de plataformas
        """
        sensors = self.get_all_sensors()
        platforms = sorted(list(set(s.platform for s in sensors)))
        return platforms

    def get_sensor_types(self) -> List[str]:
        """
        Retorna lista de tipos de sensores.

        Returns:
            Lista de tipos
        """
        sensors = self.get_all_sensors()
        types = sorted(list(set(s.sensor_type for s in sensors)))
        return types


def create_sensor_manager() -> SensorManager:
    """Factory para criar instância de SensorManager"""
    return SensorManager()
