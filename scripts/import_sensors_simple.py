"""
Script simplificado para importar sensores do arquivo sensor_paths_buzios.json
para o SafePlan (não depende de clr/pythonnet).

Uso:
    python scripts/import_sensors_simple.py

Este script:
1. Lê o arquivo sensor_paths_buzios.json gerado por discover_sensor_paths.py
2. Para cada sensor identificado:
   - Configura thresholds padrão baseados no tipo de sensor
   - Cria no banco de dados SafePlan com regras de alerta automáticas
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
from src.data.database import DatabaseManager, init_database
from src.sensors.sensor_manager import create_sensor_manager

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
        'upper_critical': 100,
        'unit': 'ppm'
    },
    'CH4_PLUME': {
        'lower_ok': 0,
        'lower_warning': 10,
        'upper_warning': 50,
        'upper_critical': 100,
        'unit': 'ppm'
    },
    'H2S': {
        'lower_ok': 0,
        'lower_warning': 1,
        'upper_warning': 10,
        'upper_critical': 20,
        'unit': 'ppm'
    },
    'CO2': {
        'lower_ok': 0,
        'lower_warning': 100,
        'upper_warning': 5000,
        'upper_critical': 10000,
        'unit': 'ppm'
    },
    'SMOKE': {
        'lower_ok': 0,
        'lower_warning': 10,
        'upper_warning': 50,
        'upper_critical': 100,
        'unit': 'obscuration %'
    },
    'FLAME': {
        'lower_ok': 0,
        'lower_warning': 1,
        'upper_warning': 2,
        'upper_critical': 3,
        'unit': 'level'
    },
    'TEMPERATURE': {
        'lower_ok': -10,
        'lower_warning': 20,
        'upper_warning': 60,
        'upper_critical': 80,
        'unit': '°C'
    },
    'H2': {
        'lower_ok': 0,
        'lower_warning': 10,
        'upper_warning': 100,
        'upper_critical': 500,
        'unit': 'ppm'
    },
    'O2': {
        'lower_ok': 19,
        'lower_warning': 18,
        'upper_warning': 22,
        'upper_critical': 25,
        'unit': '%'
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


def import_sensors():
    """Importa sensores do arquivo JSON para o SafePlan"""
    print("\n" + "="*80)
    print("SafePlan - Importação de Sensores (Arquivo JSON)")
    print("="*80 + "\n")

    try:
        # Inicializa banco
        print("[1/3] Inicializando banco de dados...")
        init_database(Config.DATABASE_URL)
        db = DatabaseManager(Config.DATABASE_URL)
        print("✓ Banco inicializado\n")

        # Carrega mapeamento
        print("[2/3] Carregando mapeamento de sensores...")
        mapping = load_sensor_mapping()
        if not mapping:
            return False

        print(f"✓ {mapping['total_sensors']} sensores para importar")
        
        # Extrai plataformas e tipos únicos
        platforms = set(s['platform'] for s in mapping['sensors'])
        sensor_types = set(s['sensor_type'] for s in mapping['sensors'])
        print(f"  Plataformas: {', '.join(sorted(platforms))}")
        print(f"  Tipos: {', '.join(sorted(sensor_types))}\n")

        # Importa sensores
        print("[3/3] Importando sensores...")
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

                # Obtém thresholds padrão
                thresholds = DEFAULT_THRESHOLDS.get(sensor_type, DEFAULT_THRESHOLDS['CH4_POINT'])
                unit = thresholds.get('unit', 'N/A')

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
                    print(f"✓ [{idx}/{len(mapping['sensors'])}] {internal_name} ({unit})")
                    imported_count += 1

                    # Cria alert rules padrão (Warning + Critical)
                    try:
                        sensor_mgr.create_alert_rule(
                            sensor_id=sensor.sensor_id,
                            condition_type='THRESHOLD',
                            severity_level=3,  # Warning (Danger)
                            threshold_value=thresholds['upper_warning']
                        )
                        sensor_mgr.create_alert_rule(
                            sensor_id=sensor.sensor_id,
                            condition_type='THRESHOLD',
                            severity_level=4,  # Critical
                            threshold_value=thresholds['upper_critical']
                        )
                    except Exception as e:
                        logger.warning(f"Erro ao criar regras de alerta para {internal_name}: {e}")

                else:
                    print(f"⚠ [{idx}/{len(mapping['sensors'])}] Falha: {internal_name}")
                    skipped_count += 1

            except Exception as e:
                logger.error(f"Erro ao importar sensor {idx}: {e}")
                print(f"✗ [{idx}/{len(mapping['sensors'])}] Erro: {str(e)}")
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
            print(f"✅ {imported_count} sensores importados com sucesso!")
            print("\nPróximos passos:")
            print("1. Acesse o dashboard: streamlit run app/main.py")
            print("2. Vá para aba 'Configuration' → 'List Sensors' para verificar")
            print("3. Ajuste os thresholds se necessário")
            print("4. Vá para 'Predictions' → 'Training' para treinar modelos ML")
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
