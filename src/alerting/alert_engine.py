"""
Alert Engine - State machine para gerenciar alertas.
Responsável por criar, atualizar e resolver alertas baseado em avaliações.
"""
import logging
from datetime import datetime
from typing import List, Optional, Dict
from enum import Enum

from src.data.database import get_db_manager
from src.data.repositories import RepositoryFactory
from src.data.models import AlertHistory, AlertDefinition

logger = logging.getLogger(__name__)


class AlertStatus(Enum):
    """Estados possíveis de um alerta"""
    ACTIVE = "ACTIVE"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RESOLVED = "RESOLVED"


class AlertSeverity(Enum):
    """Níveis de severidade de alertas"""
    OK = 1
    WARNING = 2
    DANGER = 3
    CRITICAL = 4

    @classmethod
    def from_int(cls, value: int):
        """Converte int para enum"""
        for member in cls:
            if member.value == value:
                return member
        raise ValueError(f"Severidade inválida: {value}")

    def label(self) -> str:
        """Retorna label para exibição"""
        labels = {
            1: "OK",
            2: "⚠️ AVISO",
            3: "🔴 PERIGO",
            4: "🚨 CRÍTICO"
        }
        return labels.get(self.value, "DESCONHECIDO")


class AlertCondition(Enum):
    """Tipos de condição que disparam alertas"""
    THRESHOLD = "THRESHOLD"
    ANOMALY = "ANOMALY"
    FORECAST = "FORECAST"


class AlertEngine:
    """
    Engine que gerencia ciclo de vida de alertas.
    Implementa state machine: NEW → ACTIVE → ACKNOWLEDGED/RESOLVED
    """

    def __init__(self):
        """Inicializa AlertEngine"""
        self.db_manager = get_db_manager()

    def evaluate_and_trigger(self, sensor_id: int, current_value: float,
                            alert_definitions: List[AlertDefinition],
                            anomaly_score: Optional[float] = None,
                            forecast_value: Optional[float] = None) -> List[AlertHistory]:
        """
        Avalia valor do sensor contra definições de alertas.
        Cria novos alertas se condições forem violadas.

        Args:
            sensor_id: ID do sensor
            current_value: Valor atual do sensor
            alert_definitions: Lista de definições de alerta para este sensor
            anomaly_score: Score de anomalia (0-1)
            forecast_value: Valor predito pelo forecaster

        Returns:
            Lista de alertas criados ou atualizados
        """
        triggered_alerts = []
        session = self.db_manager.get_session()

        try:
            repos = RepositoryFactory(session)
            alert_def_repo = repos.alert_definition()
            alert_history_repo = repos.alert_history()

            # Check each alert definition
            for alert_def in alert_definitions:
                if not alert_def.enabled:
                    continue

                # Determine if alert should be triggered
                should_trigger = False
                trigger_reason = ""

                if alert_def.condition_type == AlertCondition.THRESHOLD.value:
                    should_trigger, trigger_reason = self._check_threshold(
                        current_value, alert_def
                    )

                elif alert_def.condition_type == AlertCondition.ANOMALY.value:
                    if anomaly_score is not None:
                        should_trigger, trigger_reason = self._check_anomaly(
                            anomaly_score, alert_def
                        )

                elif alert_def.condition_type == AlertCondition.FORECAST.value:
                    if forecast_value is not None:
                        should_trigger, trigger_reason = self._check_forecast(
                            forecast_value, current_value, alert_def
                        )

                # Create or update alert
                if should_trigger:
                    alert = self._create_or_update_alert(
                        alert_history_repo,
                        alert_def,
                        sensor_id,
                        current_value,
                        alert_def.severity_level,
                        trigger_reason
                    )
                    triggered_alerts.append(alert)
                    logger.info(f"✓ Alerta criado: {alert.alert_id} (sensor={sensor_id}, "
                              f"severity={alert.severity_level}, reason={trigger_reason})")

                else:
                    # Check if we need to resolve existing alert
                    self._resolve_existing_alert(alert_history_repo, alert_def, sensor_id)

            session.commit()

        except Exception as e:
            logger.error(f"Erro ao avaliar alertas para sensor {sensor_id}: {e}")
            session.rollback()
        finally:
            session.close()

        return triggered_alerts

    def _check_threshold(self, value: float, alert_def: AlertDefinition) -> tuple:
        """
        Verifica se valor viola threshold definido.

        Args:
            value: Valor do sensor
            alert_def: Definição do alerta

        Returns:
            Tuple (should_trigger: bool, reason: str)
        """
        try:
            # Critical threshold (upper limit)
            if alert_def.threshold_value is not None:
                if value > alert_def.threshold_value:
                    reason = f"Valor {value} excede threshold {alert_def.threshold_value}"
                    return True, reason

            return False, ""

        except Exception as e:
            logger.error(f"Erro ao verificar threshold: {e}")
            return False, str(e)

    def _check_anomaly(self, anomaly_score: float, alert_def: AlertDefinition) -> tuple:
        """
        Verifica se anomaly score indica anomalia.

        Args:
            anomaly_score: Score de anomalia (0-1)
            alert_def: Definição do alerta

        Returns:
            Tuple (should_trigger: bool, reason: str)
        """
        try:
            threshold = alert_def.anomaly_threshold or 0.7

            if anomaly_score > threshold:
                reason = f"Anomalia detectada (score={anomaly_score:.2f}, threshold={threshold})"
                return True, reason

            return False, ""

        except Exception as e:
            logger.error(f"Erro ao verificar anomalia: {e}")
            return False, str(e)

    def _check_forecast(self, forecast_value: float, current_value: float,
                       alert_def: AlertDefinition) -> tuple:
        """
        Verifica se forecast indica tendência preocupante.

        Args:
            forecast_value: Valor predito
            current_value: Valor atual
            alert_def: Definição do alerta

        Returns:
            Tuple (should_trigger: bool, reason: str)
        """
        try:
            # Simple trend check: se forecast está em direção ruim
            if alert_def.threshold_value is not None:
                if forecast_value > alert_def.threshold_value:
                    percent_increase = ((forecast_value - current_value) / current_value) * 100
                    reason = (f"Previsão indica aumento perigoso "
                            f"(atual={current_value:.2f}, previsto={forecast_value:.2f}, "
                            f"+{percent_increase:.1f}%)")
                    return True, reason

            return False, ""

        except Exception as e:
            logger.error(f"Erro ao verificar forecast: {e}")
            return False, str(e)

    def _create_or_update_alert(self, alert_repo, alert_def: AlertDefinition,
                               sensor_id: int, sensor_value: float,
                               severity: int, reason: str) -> AlertHistory:
        """
        Cria novo alerta ou atualiza existente.
        Evita duplicatas (deduplicação).

        Args:
            alert_repo: Repository de alertas
            alert_def: Definição do alerta
            sensor_id: ID do sensor
            sensor_value: Valor do sensor
            severity: Nível de severidade
            reason: Razão do alerta

        Returns:
            AlertHistory object
        """
        # Check if alert already active
        active_alerts = alert_repo.get_active_by_sensor(sensor_id)

        for active_alert in active_alerts:
            if active_alert.alert_def_id == alert_def.alert_def_id:
                # Alert already exists, just update value
                active_alert.sensor_value = sensor_value
                active_alert.notes = reason
                return active_alert

        # Create new alert
        alert = alert_repo.create(
            alert_def_id=alert_def.alert_def_id,
            sensor_id=sensor_id,
            sensor_value=sensor_value,
            severity_level=severity
        )

        alert.notes = reason
        return alert

    def _resolve_existing_alert(self, alert_repo, alert_def: AlertDefinition,
                               sensor_id: int):
        """
        Resolve alertas existentes se condição for atendida.

        Args:
            alert_repo: Repository de alertas
            alert_def: Definição do alerta
            sensor_id: ID do sensor
        """
        try:
            active_alerts = alert_repo.get_active_by_sensor(sensor_id)

            for alert in active_alerts:
                if alert.alert_def_id == alert_def.alert_def_id:
                    logger.info(f"✓ Alerta resolvido: {alert.alert_id}")
                    alert_repo.resolve(alert.alert_id)

        except Exception as e:
            logger.error(f"Erro ao resolver alerta: {e}")

    def acknowledge_alert(self, alert_id: int, notes: str = None) -> Optional[AlertHistory]:
        """
        Marca alerta como reconhecido (acknowledged).

        Args:
            alert_id: ID do alerta
            notes: Notas opcionais do reconhecimento

        Returns:
            AlertHistory atualizado ou None se erro
        """
        session = self.db_manager.get_session()

        try:
            repos = RepositoryFactory(session)
            alert_repo = repos.alert_history()

            alert = alert_repo.acknowledge(alert_id)

            if alert and notes:
                alert.notes = notes

            session.commit()
            logger.info(f"✓ Alerta {alert_id} reconhecido")
            return alert

        except Exception as e:
            logger.error(f"Erro ao reconhecer alerta: {e}")
            session.rollback()
            return None
        finally:
            session.close()

    def resolve_alert(self, alert_id: int) -> Optional[AlertHistory]:
        """
        Marca alerta como resolvido.

        Args:
            alert_id: ID do alerta

        Returns:
            AlertHistory atualizado ou None se erro
        """
        session = self.db_manager.get_session()

        try:
            repos = RepositoryFactory(session)
            alert_repo = repos.alert_history()

            alert = alert_repo.resolve(alert_id)
            session.commit()
            logger.info(f"✓ Alerta {alert_id} resolvido")
            return alert

        except Exception as e:
            logger.error(f"Erro ao resolver alerta: {e}")
            session.rollback()
            return None
        finally:
            session.close()

    def get_active_alerts(self) -> List[AlertHistory]:
        """
        Retorna todos os alertas ativos no sistema.

        Returns:
            Lista de AlertHistory ativos
        """
        session = self.db_manager.get_session()

        try:
            repos = RepositoryFactory(session)
            alert_repo = repos.alert_history()

            # Get recent alerts (last 1000)
            alerts = alert_repo.get_recent(limit=1000)
            active = [a for a in alerts if a.status == AlertStatus.ACTIVE.value]

            return active

        except Exception as e:
            logger.error(f"Erro ao buscar alertas ativos: {e}")
            return []
        finally:
            session.close()

    def get_alerts_by_sensor(self, sensor_id: int, limit: int = 100) -> List[AlertHistory]:
        """
        Retorna alertas de um sensor específico.

        Args:
            sensor_id: ID do sensor
            limit: Limite de registros

        Returns:
            Lista de AlertHistory
        """
        session = self.db_manager.get_session()

        try:
            repos = RepositoryFactory(session)
            alert_repo = repos.alert_history()

            alerts = alert_repo.get_recent(limit=min(limit, 1000))
            sensor_alerts = [a for a in alerts if a.sensor_id == sensor_id]

            return sensor_alerts

        except Exception as e:
            logger.error(f"Erro ao buscar alertas do sensor {sensor_id}: {e}")
            return []
        finally:
            session.close()

    def get_alert_statistics(self) -> Dict:
        """
        Retorna estatísticas de alertas.

        Returns:
            Dict com contadores de alertas por severidade e status
        """
        try:
            active_alerts = self.get_active_alerts()

            stats = {
                'total_active': len(active_alerts),
                'critical': len([a for a in active_alerts if a.severity_level == 4]),
                'danger': len([a for a in active_alerts if a.severity_level == 3]),
                'warning': len([a for a in active_alerts if a.severity_level == 2]),
                'by_status': {}
            }

            return stats

        except Exception as e:
            logger.error(f"Erro ao calcular estatísticas: {e}")
            return {
                'total_active': 0,
                'critical': 0,
                'danger': 0,
                'warning': 0
            }


def create_alert_engine() -> AlertEngine:
    """Factory para criar instância de AlertEngine"""
    return AlertEngine()
