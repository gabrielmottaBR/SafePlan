"""
Script para importar sensores descobertos do AF para o SafePlan.

Uso:
    python scripts/import_sensors_from_af.py

Este script:
1. Lê o arquivo sensor_paths_buzios.json gerado por discover_sensor_paths.py
2. Para cada sensor identificado:
   - Obtém o valor corrente e unidade de medida
   - Configura thresholds padrão baseados no tipo de sensor
   - Cria no banco de dados SafePlan
"""
import os
import sys
import json
import logging
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from config.settings import Config
from src.data.database import init_database
from src.data.repositories import RepositoryFactory
from src.sensors.sensor_manager import create_sensor_manager
from src.pi_server import gideaoPI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Thresholds padrão por tipo de sensor
DEFAULT_THRESHOLDS = {
    'CH4_POINT': {
        'lower_ok': 0,
        'lower_warning': 5,
        'upper_warning': 50,
        'upper_critical': 100
    },
    'CH4_PLUME': {
        'lower_ok': 0,
        'lower_warning': 10,
        'upper_warning': 50,
        'upper_critical': 100
    },
    'H2S': {
        'lower_ok': 0,
        'lower_warning': 1,
        'upper_warning': 10,
        'upper_critical': 20
    },
    'CO2': {
        'lower_ok': 0,
        'lower_warning': 100,
        'upper_warning': 5000,
        'upper_critical': 10000
    },
    'SMOKE': {
        'lower_ok': 0,
        'lower_warning': 10,
        'upper_warning': 50,
        'upper_critical': 100
    },
    'FLAME': {
        'lower_ok': 0,
        'lower_warning': 1,
        'upper_warning': 2,
        'upper_critical': 3
    },
    'TEMPERATURE': {
        'lower_ok': -10,
        'lower_warning': 20,
        'upper_warning': 60,
        'upper_critical': 80
    },
    'H2': {
        'lower_ok': 0,
        'lower_warning': 10,
        'upper_warning': 100,
        'upper_critical': 500
    },
    'O2': {
        'lower_ok': 19,
        'lower_warning': 18,
        'upper_warning': 22,
        'upper_critical': 25
    }
}


def load_sensor_mapping():
    """Carrega mapeamento de sensores descobertos"""
    config_file = os.path.join(
        project_root,
        'config',
        'sensor_paths_buzios.json'
    )

    if not os.path.exists(config_file):
        logger.error(f"Arquivo não encontrado: {config_file}")
        logger.info("Execute primeiro: python scripts/discover_sensor_paths.py")
        return None

    with open(config_file, 'r') as f:
        return json.load(f)


def get_sensor_unit(db, sensor_path):
    """Obtém unidade de medida do sensor no AF"""
    try:
        from src.pi_server import gideaoPI
        unit = gideaoPI.getUM(db, sensor_path)
        return unit if unit else 'N/A'
    except Exception as e:
        logger.warning(f"Erro ao obter unidade para {sensor_path}: {e}")
        return 'N/A'


def import_sensors():
    """Importa sensores do AF para o SafePlan"""
    print("\n" + "="*80)
    print("SafePlan - Importação de Sensores do AF Server")
    print("="*80 + "\n")

    try:
        # Inicializa banco
        print("[1/4] Inicializando banco de dados...")
        init_database(Config.DATABASE_URL)
        print("✓ Banco inicializado\n")

        # Carrega mapeamento
        print("[2/4] Carregando mapeamento de sensores...")
        mapping = load_sensor_mapping()
        if not mapping:
            return False

        print(f"✓ {mapping['total_sensors']} sensores para importar\n")

        # Conecta ao AF
        print("[3/4] Conectando ao AF Server...")
        af_server = gideaoPI.getServidor('SAURIOPIAF02', 'AF')
        db = gideaoPI.getAFDataBase('DB_BUZIOS_SENSORES', af_server)
        print("✓ Conectado\n")

        # Importa sensores
        print("[4/4] Importando sensores...")
        print("-" * 80)

        sensor_mgr = create_sensor_manager()
        imported_count = 0
        skipped_count = 0
        error_count = 0

        for idx, sensor_info in enumerate(mapping['sensors'], 1):
            try:
                sensor_path = sensor_info['path']
                platform = sensor_info['platform']
                sensor_type = sensor_info['sensor_type']
                sensor_name = sensor_info['name']

                # Nome interno (único)
                internal_name = f"{platform}_{sensor_type}_{idx}"

                # Display name
                display_name = f"{sensor_name} ({platform})"

                # Obtém unidade
                unit = get_sensor_unit(db, sensor_path)

                # Obtém thresholds padrão
                thresholds = DEFAULT_THRESHOLDS.get(sensor_type, DEFAULT_THRESHOLDS['CH4_POINT'])

                # Cria sensor
                sensor = sensor_mgr.create_sensor(
                    internal_name=internal_name,
                    display_name=display_name,
                    sensor_type=sensor_type,
                    platform=platform,
                    unit=unit,
                    pi_server_tag=sensor_path,
                    lower_ok_limit=thresholds['lower_ok'],
                    lower_warning_limit=thresholds['lower_warning'],
                    upper_warning_limit=thresholds['upper_warning'],
                    upper_critical_limit=thresholds['upper_critical']
                )

                if sensor:
                    print(f"✓ [{idx}/{len(mapping['sensors'])}] {internal_name}")
                    imported_count += 1

                    # Cria alert rules padrão
                    sensor_mgr.create_alert_rule(
                        sensor_id=sensor.sensor_id,
                        condition_type='THRESHOLD',
                        severity_level=3,
                        threshold_value=thresholds['upper_warning']
                    )
                    sensor_mgr.create_alert_rule(
                        sensor_id=sensor.sensor_id,
                        condition_type='THRESHOLD',
                        severity_level=4,
                        threshold_value=thresholds['upper_critical']
                    )
                else:
                    print(f"⚠ [{idx}/{len(mapping['sensors'])}] Falha: {internal_name}")
                    skipped_count += 1

            except Exception as e:
                logger.error(f"Erro ao importar sensor {idx}: {e}")
                error_count += 1

        print("-" * 80 + "\n")

        # Resumo
        print("="*80)
        print("RESUMO DA IMPORTAÇÃO")
        print("="*80)
        print(f"Total processado: {len(mapping['sensors'])}")
        print(f"✓ Importados com sucesso: {imported_count}")
        print(f"⚠ Pulados/Erros: {skipped_count + error_count}")
        print("="*80 + "\n")

        if imported_count > 0:
            print("✓ Sensores importados com sucesso!")
            print("\nPróximos passos:")
            print("1. Acesse o dashboard: streamlit run app/main.py")
            print("2. Vá para aba 'Configuration' para verificar sensores")
            print("3. Se necessário, ajuste os thresholds para cada sensor")
            print("4. Execute o teste de integração: python scripts/test_phase2.py")
            return True
        else:
            print("✗ Nenhum sensor foi importado")
            return False

    except Exception as e:
        logger.error(f"Erro em import_sensors: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = import_sensors()
    sys.exit(0 if success else 1)
