"""
Database connection and session management for SQLite backend.
Handles database initialization, connection pooling, and session lifecycle.
"""
import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from src.data.models import Base
from src.utils.config import get_config

logger = None


class DatabaseManager:
    """
    Gerencia conexão com banco de dados SQLite.
    Fornece métodos para criar sessões e executar operações.
    """

    def __init__(self, database_url: str = None):
        """
        Inicializa DatabaseManager com URL do banco de dados.

        Args:
            database_url: URL de conexão SQLite (ex: sqlite:///./safeplan.db)
                         Se None, usa variável de ambiente DATABASE_URL
        """
        if database_url is None:
            database_url = os.getenv('DATABASE_URL', 'sqlite:///./safeplan.db')

        self.database_url = database_url
        self.engine = None
        self.SessionLocal = None
        self._init_engine()

    def _init_engine(self):
        """Inicializa SQLAlchemy engine com SQLite"""
        # Para SQLite em arquivo
        if self.database_url.startswith('sqlite:///'):
            # Cria arquivo do DB se não existir
            db_file = self.database_url.replace('sqlite:///', '')
            db_dir = os.path.dirname(db_file)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)

            self.engine = create_engine(
                self.database_url,
                connect_args={"check_same_thread": False},
                echo=os.getenv('DATABASE_ECHO_SQL', 'false').lower() == 'true'
            )
        else:
            # Para outros databases (PostgreSQL, etc)
            self.engine = create_engine(
                self.database_url,
                echo=os.getenv('DATABASE_ECHO_SQL', 'false').lower() == 'true',
                pool_size=20,
                max_overflow=40
            )

        # Configura eventos Foreign Key para SQLite
        if self.database_url.startswith('sqlite:'):
            @event.listens_for(self.engine, 'connect')
            def set_sqlite_pragma(dbapi_conn, connection_record):
                cursor = dbapi_conn.cursor()
                cursor.execute('PRAGMA foreign_keys=ON')
                cursor.close()

        # Cria sessionmaker
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

    def create_all_tables(self):
        """
        Cria todas as tabelas definidas em Base.metadata.
        Deve ser executado uma vez durante inicialização.
        """
        Base.metadata.create_all(bind=self.engine)

    def drop_all_tables(self):
        """
        Remove todas as tabelas (CUIDADO: Destrutivo!).
        Use apenas em desenvolvimento.
        """
        Base.metadata.drop_all(bind=self.engine)

    def get_session(self) -> Session:
        """
        Retorna uma nova sessão do banco de dados.
        Use como context manager: with db_manager.get_session() as session: ...

        Returns:
            SQLAlchemy Session object
        """
        return self.SessionLocal()

    def close_session(self, session: Session):
        """
        Fecha uma sessão do banco de dados.

        Args:
            session: Session object a ser fechada
        """
        if session:
            session.close()

    def health_check(self) -> bool:
        """
        Verifica se a conexão com o banco está funcionando.

        Returns:
            True se conexão está OK, False caso contrário
        """
        try:
            with self.engine.connect() as conn:
                conn.execute("SELECT 1")
            return True
        except Exception as e:
            print(f"Database health check failed: {e}")
            return False


# Global database manager instance
_db_manager = None


def init_database(database_url: str = None) -> DatabaseManager:
    """
    Inicializa o gerenciador de banco de dados global.
    Deve ser chamado uma vez na inicialização da aplicação.

    Args:
        database_url: URL de conexão SQLite (opcional)

    Returns:
        DatabaseManager instance
    """
    global _db_manager
    _db_manager = DatabaseManager(database_url)
    _db_manager.create_all_tables()
    return _db_manager


def get_db_manager() -> DatabaseManager:
    """
    Retorna a instância global de DatabaseManager.

    Returns:
        DatabaseManager instance

    Raises:
        RuntimeError: Se database não foi inicializado
    """
    global _db_manager
    if _db_manager is None:
        raise RuntimeError(
            "Database not initialized. Call init_database() first."
        )
    return _db_manager


def get_db_session() -> Session:
    """
    Convenience function para obter nova sessão de banco.

    Returns:
        SQLAlchemy Session object
    """
    return get_db_manager().get_session()
