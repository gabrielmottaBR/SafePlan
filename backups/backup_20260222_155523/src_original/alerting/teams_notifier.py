"""
Teams Notifier - Envia notificações de alertas para Microsoft Teams via webhook.
Implementa retry logic e logging de notificações.
"""
import logging
import time
import json
from typing import Optional
from datetime import datetime
import requests

from config.settings import Config
from src.data.database import get_db_manager
from src.data.repositories import RepositoryFactory
from src.data.models import AlertHistory

logger = logging.getLogger(__name__)


class TeamsNotifier:
    """
    Envia notificações de alertas para Microsoft Teams via Incoming Webhook.
    """

    def __init__(self, webhook_url: str = None):
        """
        Inicializa TeamsNotifier.

        Args:
            webhook_url: URL do webhook do Teams (opcional, usa Config se None)
        """
        self.webhook_url = webhook_url or Config.TEAMS_WEBHOOK_URL
        self.max_retries = Config.ALERT_RETRY_MAX_ATTEMPTS
        self.retry_backoff = Config.ALERT_RETRY_BACKOFF_SECONDS

        if not self.webhook_url:
            logger.warning("Teams webhook URL não configurada (TEAMS_WEBHOOK_URL)")

    def notify_alert(self, alert: AlertHistory) -> bool:
        """
        Envia notificação de alerta para Teams.

        Args:
            alert: AlertHistory object

        Returns:
            True se enviado com sucesso, False caso contrário
        """
        if not self.webhook_url:
            logger.warning("Webhook Teams não configurado, pulando notificação")
            return False

        # Format message
        message = self._build_alert_message(alert)

        # Send with retry
        success = self._send_with_retry(message)

        # Log notification
        self._log_notification(alert, success, message)

        return success

    def _build_alert_message(self, alert: AlertHistory) -> dict:
        """
        Constrói mensagem formatada para Teams.

        Args:
            alert: AlertHistory object

        Returns:
            Dict com formato de Adaptive Card para Teams
        """
        # Sensor info
        sensor = alert.sensor if hasattr(alert, 'sensor') else None
        sensor_name = sensor.display_name if sensor else f"Sensor {alert.sensor_id}"
        sensor_type = sensor.sensor_type if sensor else "Desconhecido"
        platform = sensor.platform if sensor else "Desconhecido"

        # Alert info
        severity_labels = {
            1: "OK",
            2: "⚠️ AVISO",
            3: "🔴 PERIGO",
            4: "🚨 CRÍTICO"
        }
        severity_label = severity_labels.get(alert.severity_level, "DESCONHECIDO")

        severity_colors = {
            1: "0070C0",
            2: "FFB900",
            3: "D13438",
            4: "A4373A"
        }
        color = severity_colors.get(alert.severity_level, "000000")

        # Build Adaptive Card
        card = {
            "@type": "MessageCard",
            "@context": "https://schema.org/extensions",
            "summary": f"{severity_label} - {sensor_name}",
            "themeColor": color,
            "sections": [
                {
                    "activityTitle": f"{severity_label} - SafePlan Alert",
                    "activitySubtitle": f"Sensor: {sensor_name}",
                    "facts": [
                        {
                            "name": "Plataforma:",
                            "value": platform
                        },
                        {
                            "name": "Tipo de Sensor:",
                            "value": sensor_type
                        },
                        {
                            "name": "Valor Atual:",
                            "value": f"{alert.sensor_value:.2f} {sensor.unit if sensor else ''}"
                        },
                        {
                            "name": "Severidade:",
                            "value": severity_label
                        },
                        {
                            "name": "Hora do Alerta:",
                            "value": alert.triggered_at.strftime("%d/%m/%Y %H:%M:%S")
                        },
                        {
                            "name": "Notas:",
                            "value": alert.notes or "N/A"
                        }
                    ],
                    "markdown": True
                }
            ],
            "potentialAction": [
                {
                    "@type": "OpenUri",
                    "name": "Ver Dashboard",
                    "targets": [
                        {
                            "os": "default",
                            "uri": "http://localhost:8501"
                        }
                    ]
                }
            ]
        }

        return card

    def _send_with_retry(self, message: dict) -> bool:
        """
        Envia mensagem para Teams com retry logic.

        Args:
            message: Mensagem formatada para Teams

        Returns:
            True se sucesso, False se falha após retries
        """
        for attempt in range(self.max_retries):
            try:
                headers = {'Content-Type': 'application/json'}

                response = requests.post(
                    self.webhook_url,
                    json=message,
                    headers=headers,
                    timeout=10
                )

                if response.status_code == 200:
                    logger.info(f"✓ Notificação enviada para Teams com sucesso")
                    return True

                else:
                    logger.warning(
                        f"Teams retornou status {response.status_code}: {response.text}"
                    )

            except requests.exceptions.Timeout:
                logger.warning(f"Timeout ao conectar Teams (tentativa {attempt + 1}/{self.max_retries})")

            except requests.exceptions.ConnectionError as e:
                logger.warning(
                    f"Erro de conexão com Teams (tentativa {attempt + 1}/{self.max_retries}): {e}"
                )

            except Exception as e:
                logger.error(f"Erro ao enviar para Teams: {e}")

            # Retry with backoff
            if attempt < self.max_retries - 1:
                wait_time = self.retry_backoff * (2 ** attempt)  # Exponential backoff
                logger.info(f"Agendando retry em {wait_time}s...")
                time.sleep(wait_time)

        logger.error(f"Falha ao enviar notificação para Teams após {self.max_retries} tentativas")
        return False

    def _log_notification(self, alert: AlertHistory, success: bool, message: dict):
        """
        Registra tentativa de notificação no banco de dados.

        Args:
            alert: AlertHistory
            success: Se envio foi bem-sucedido
            message: Mensagem que foi tentada
        """
        try:
            session = get_db_manager().get_session()
            repos = RepositoryFactory(session)
            notif_repo = repos.notification_log()

            notification = notif_repo.create(
                alert_id=alert.alert_id,
                channel='TEAMS',
                message=json.dumps(message),
                status='SENT' if success else 'FAILED'
            )

            if success:
                notif_repo.mark_sent(notification.notification_id, response_code=200)
            else:
                notif_repo.mark_failed(notification.notification_id, error_message="Falha após retries")

            session.close()

        except Exception as e:
            logger.error(f"Erro ao registrar log de notificação: {e}")

    def notify_critical_alerts(self) -> int:
        """
        Envia notificações para todos os alertas críticos/perigo ainda não notificados.

        Returns:
            Número de notificações enviadas
        """
        try:
            session = get_db_manager().get_session()
            repos = RepositoryFactory(session)
            alert_repo = repos.alert_history()
            notif_repo = repos.notification_log()

            # Get recent critical alerts
            recent_alerts = alert_repo.get_recent(limit=500)
            critical_alerts = [
                a for a in recent_alerts
                if a.severity_level >= 3 and a.status == 'ACTIVE'
            ]

            notified_count = 0

            for alert in critical_alerts:
                # Check if already notified
                notifications = notif_repo.get_by_alert(alert.alert_id)

                if notifications:
                    # Already notified, skip
                    continue

                # Send notification
                if self.notify_alert(alert):
                    notified_count += 1

            session.close()
            return notified_count

        except Exception as e:
            logger.error(f"Erro ao enviar notificações críticas: {e}")
            return 0

    @staticmethod
    def test_webhook(webhook_url: str) -> bool:
        """
        Testa a conectividade do webhook.

        Args:
            webhook_url: URL do webhook

        Returns:
            True se webhook está acessível
        """
        try:
            test_message = {
                "@type": "MessageCard",
                "@context": "https://schema.org/extensions",
                "summary": "SafePlan - Teste de Webhook",
                "themeColor": "0070C0",
                "sections": [
                    {
                        "activityTitle": "SafePlan - Teste de Webhook",
                        "activitySubtitle": "Webhook configurado corretamente",
                        "facts": [
                            {
                                "name": "Status:",
                                "value": "✓ Funcionando"
                            },
                            {
                                "name": "Timestamp:",
                                "value": datetime.utcnow().isoformat()
                            }
                        ]
                    }
                ]
            }

            response = requests.post(
                webhook_url,
                json=test_message,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )

            return response.status_code == 200

        except Exception as e:
            logger.error(f"Erro ao testar webhook: {e}")
            return False


def create_teams_notifier() -> TeamsNotifier:
    """Factory para criar instância de TeamsNotifier"""
    return TeamsNotifier()
