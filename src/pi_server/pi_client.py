"""
PI Server client wrapper around gideaoPI library.
Handles connection, authentication, and error handling for PI Server access.
"""
import logging
from typing import Optional, List, Tuple
from datetime import datetime
from config.settings import Config

logger = logging.getLogger(__name__)


class PIServerClient:
    """
    Cliente para PI Server usando gideaoPI.
    Fornece métodos para conectar, autenticar e buscar dados.
    """

    def __init__(self, host: str = None, username: str = None, password: str = None,
                 archive: str = None, timeout: int = None):
        """
        Inicializa client do PI Server.

        Args:
            host: Hostname do PI Server
            username: Usuário para autenticação
            password: Senha para autenticação
            archive: Nome do archive (ex: DEFAULT)
            timeout: Timeout para requisições em segundos
        """
        self.host = host or Config.PI_SERVER_HOST
        self.username = username or Config.PI_SERVER_USERNAME
        self.password = password or Config.PI_SERVER_PASSWORD
        self.archive = archive or Config.PI_DATA_ARCHIVE
        self.timeout = timeout or Config.PI_REQUEST_TIMEOUT

        self.servidor = None
        self._connected = False

    def connect(self) -> bool:
        """
        Conecta ao PI Server usando gideao_pi.

        Returns:
            True se conexão bem-sucedida, False caso contrário
        """
        try:
            import gideao_pi as gp

            logger.info(f"Conectando ao PI Server: {self.host}")
            self.servidor = gp.getServidor(self.host, self.archive)

            if self.servidor is None:
                logger.error(f"Falha ao conectar ao PI Server {self.host}")
                self._connected = False
                return False

            self._connected = True
            logger.info(f"✓ Conectado ao PI Server: {self.host}")
            return True

        except ImportError:
            logger.error("gideao_pi não instalado. Instale com: pip install gideao_pi")
            return False
        except Exception as e:
            logger.error(f"Erro ao conectar ao PI Server: {e}")
            return False

    def is_connected(self) -> bool:
        """Retorna estado da conexão"""
        return self._connected

    def get_interpolated_data(self, tag: str, start_date: datetime, end_date: datetime,
                             interval: str = '10m', numeric_only: bool = False) -> Optional[dict]:
        """
        Busca dados interpolados de um tag do PI Server.

        Args:
            tag: Nome do tag no PI Server
            start_date: Data/hora de início (format: 'MM/DD/YYYY' ou datetime)
            end_date: Data/hora de fim
            interval: Intervalo de interpolação (ex: '10m', '1h')
            numeric_only: Se True, retorna apenas valores numéricos

        Returns:
            Dictionary com dados interpolados ou None se erro
        """
        try:
            if not self._connected:
                logger.warning("Não conectado ao PI Server. Tentando reconectar...")
                if not self.connect():
                    return None

            import gideaoPI as gp
            import pandas as pd

            # Convert datetime to string format se necessário
            if isinstance(start_date, datetime):
                start_str = start_date.strftime('%m/%d/%Y')
            else:
                start_str = start_date

            if isinstance(end_date, datetime):
                end_str = end_date.strftime('%m/%d/%Y')
            else:
                end_str = end_date

            logger.debug(f"Buscando dados de {tag} de {start_str} a {end_str}")

            # Call gideaoPI
            df = gp.getValoresInterpolados(
                self.servidor,
                tag,
                start_str,
                end_str,
                interval,
                numeric_only
            )

            if df is None or df.empty:
                logger.warning(f"Nenhum dado retornado para tag: {tag}")
                return None

            logger.debug(f"✓ Dados obtidos para {tag}: {len(df)} registros")
            return df

        except Exception as e:
            logger.error(f"Erro ao buscar dados interpolados para {tag}: {e}")
            return None

    def get_raw_data(self, tag: str, start_date: datetime, end_date: datetime) -> Optional[dict]:
        """
        Busca dados brutos (não interpolados) de um tag.

        Args:
            tag: Nome do tag no PI Server
            start_date: Data/hora de início
            end_date: Data/hora de fim

        Returns:
            DataFrame com dados brutos ou None se erro
        """
        try:
            if not self._connected:
                if not self.connect():
                    return None

            import gideaoPI as gp

            if isinstance(start_date, datetime):
                start_str = start_date.strftime('%m/%d/%Y')
            else:
                start_str = start_date

            if isinstance(end_date, datetime):
                end_str = end_date.strftime('%m/%d/%Y')
            else:
                end_str = end_date

            logger.debug(f"Buscando dados brutos de {tag} de {start_str} a {end_str}")

            # Call gideaoPI for raw data
            df = gp.getValores(self.servidor, tag, start_str, end_str)

            if df is None or df.empty:
                logger.warning(f"Nenhum dado bruto retornado para tag: {tag}")
                return None

            logger.debug(f"✓ Dados brutos obtidos para {tag}: {len(df)} registros")
            return df

        except Exception as e:
            logger.error(f"Erro ao buscar dados brutos para {tag}: {e}")
            return None

    def get_last_value(self, tag: str) -> Optional[Tuple[float, datetime]]:
        """
        Busca o último valor de um tag.

        Args:
            tag: Nome do tag no PI Server

        Returns:
            Tuple (value, timestamp) ou None se erro
        """
        try:
            if not self._connected:
                if not self.connect():
                    return None

            import gideaoPI as gp

            logger.debug(f"Buscando último valor de {tag}")

            # Get snapshot (last value)
            value = gp.getValor(self.servidor, tag)

            if value is None:
                logger.warning(f"Nenhum valor retornado para tag: {tag}")
                return None

            # Get value with timestamp
            # Note: gideaoPI retorna apenas o valor, precisamos buscar timestamp
            # Para isso, buscamos dados interpolados do último minuto
            from datetime import datetime, timedelta

            now = datetime.utcnow()
            start = now - timedelta(minutes=1)

            df = gp.getValoresInterpolados(
                self.servidor,
                tag,
                start.strftime('%m/%d/%Y'),
                now.strftime('%m/%d/%Y'),
                '1m',
                False
            )

            if df is not None and not df.empty:
                last_row = df.iloc[-1]
                timestamp = pd.to_datetime(last_row['timestamp'])
                return (float(value), timestamp)

            return (float(value), now)

        except Exception as e:
            logger.error(f"Erro ao buscar último valor de {tag}: {e}")
            return None

    def get_multiple_tags(self, tags: List[str], start_date: datetime,
                         end_date: datetime, interval: str = '10m') -> Optional[dict]:
        """
        Busca dados de múltiplos tags simultaneamente.

        Args:
            tags: Lista de nomes de tags
            start_date: Data/hora de início
            end_date: Data/hora de fim
            interval: Intervalo de interpolação

        Returns:
            Dictionary com DataFrames para cada tag ou None se erro
        """
        try:
            if not self._connected:
                if not self.connect():
                    return None

            import pandas as pd

            result = {}

            for tag in tags:
                logger.debug(f"Buscando {tag}...")

                df = self.get_interpolated_data(
                    tag, start_date, end_date, interval, numeric_only=False
                )

                if df is not None:
                    result[tag] = df
                else:
                    logger.warning(f"Falha ao buscar {tag}")

            if not result:
                logger.error("Nenhum dado obtido para os tags solicitados")
                return None

            logger.info(f"✓ Dados obtidos para {len(result)}/{len(tags)} tags")
            return result

        except Exception as e:
            logger.error(f"Erro ao buscar múltiplos tags: {e}")
            return None

    def disconnect(self):
        """Desconecta do PI Server"""
        try:
            self._connected = False
            logger.info("Desconectado do PI Server")
        except Exception as e:
            logger.error(f"Erro ao desconectar: {e}")

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()


# Global client instance
_pi_client: Optional[PIServerClient] = None


def get_pi_client(host: str = None, username: str = None, password: str = None) -> PIServerClient:
    """
    Retorna instância global de PIServerClient.
    Se não existir, cria nova instância.

    Args:
        host: PI Server hostname
        username: Username para autenticação
        password: Password para autenticação

    Returns:
        PIServerClient instance
    """
    global _pi_client

    if _pi_client is None:
        _pi_client = PIServerClient(host, username, password)
        _pi_client.connect()

    return _pi_client


def reconnect_pi_client():
    """Reconecta ao PI Server"""
    global _pi_client
    _pi_client = None
    get_pi_client()
