"""
Script para inicializar o banco de dados SQLite.
Cria todas as tabelas e estrutura necessária.

Usage:
    python scripts/init_db.py
"""
import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from config.settings import Config
from src.data.database import DatabaseManager


def main():
    """Inicializa banco de dados"""
    print("=" * 60)
    print("SafePlan Database Initialization")
    print("=" * 60)

    # Display configuration
    print("\n[INFO] Configurações ativas:")
    config_summary = Config.get_summary()
    print(f"  Database URL: {Config.DATABASE_URL}")
    print(f"  PI Server: {Config.PI_SERVER_HOST}")
    print(f"  Debug Mode: {Config.DEBUG_MODE}")

    # Initialize database
    print("\n[INFO] Inicializando banco de dados...")
    try:
        db_manager = DatabaseManager(database_url=Config.DATABASE_URL)

        # Create all tables
        print("[INFO] Criando tabelas...")
        db_manager.create_all_tables()

        # Health check
        print("[INFO] Verificando saúde da conexão...")
        if db_manager.health_check():
            print("[SUCCESS] ✓ Banco de dados inicializado com sucesso!")
        else:
            print("[ERROR] ✗ Falha na verificação de saúde")
            return 1

        # Display database info
        print("\n[INFO] Informações do banco de dados:")
        print(f"  Localização: {Config.DATABASE_URL}")
        print(f"  Tabelas criadas:")
        print("    - sensor_config")
        print("    - sensor_readings")
        print("    - alert_definitions")
        print("    - alert_history")
        print("    - ml_predictions")
        print("    - notification_log")

        print("\n[SUCCESS] Database initialization complete!")
        print("=" * 60)
        return 0

    except Exception as e:
        print(f"\n[ERROR] Erro ao inicializar banco de dados: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
