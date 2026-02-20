"""
Script para descobrir sensores disponíveis no SAURIOPIAF02\DB_BUZIOS_SENSORES
e criar mapeamento para importação no SafePlan.

Uso:
    python scripts/discover_sensor_paths.py
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
from src.pi_server import gideaoPI
from src.pi_server.af_manager import AFDatabaseManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def discover_sensors():
    """
    Descobre todos os sensores no SAURIOPIAF02\DB_BUZIOS_SENSORES
    e cria arquivo de mapeamento
    """
    print("\n" + "="*80)
    print("SafePlan - Descoberta de Sensores do PI AF Server")
    print("="*80 + "\n")

    try:
        # Conecta ao AF Server
        print("[1/5] Conectando ao AF Server SAURIOPIAF02...")
        af_server = gideaoPI.getServidor('SAURIOPIAF02', 'AF')

        if not af_server:
            print("✗ Falha ao conectar ao AF Server")
            return False

        print("✓ Conectado com sucesso")

        # Obtém database
        print("\n[2/5] Obtendo database DB_BUZIOS_SENSORES...")
        db = gideaoPI.getAFDataBase('DB_BUZIOS_SENSORES', af_server)

        if not db:
            print("✗ Falha ao obter database")
            return False

        print("✓ Database obtido com sucesso")

        # Explora estrutura
        print("\n[3/5] Explorando estrutura da database...")
        manager = AFDatabaseManager(db)
        manager.print_structure()

        # Busca sensores
        print("[4/5] Buscando sensores de fogo/gás...")
        sensors = manager.get_sensor_paths()

        if not sensors:
            print("⚠ Nenhum sensor encontrado")
            return False

        print(f"✓ Encontrados {len(sensors)} sensores\n")

        # Cria mapeamento
        print("[5/5] Criando arquivo de mapeamento...")

        sensor_mapping = {
            'discovery_date': datetime.now().isoformat(),
            'af_server': 'SAURIOPIAF02',
            'database': 'DB_BUZIOS_SENSORES',
            'total_sensors': len(sensors),
            'sensors': []
        }

        # Organiza sensores por plataforma e tipo
        for sensor_path in sensors:
            path_upper = sensor_path.upper()

            # Identifica plataforma
            platform = 'UNKNOWN'
            for p in ['P74', 'P75', 'P76', 'P77', 'P78', 'P79', 'FPAB', 'FPAT']:
                if p in path_upper:
                    platform = p
                    break

            # Identifica tipo de sensor
            sensor_type = 'OTHER'
            if 'CH4' in path_upper:
                sensor_type = 'CH4_POINT' if 'POINT' in path_upper else 'CH4_PLUME'
            elif 'H2S' in path_upper:
                sensor_type = 'H2S'
            elif 'CO2' in path_upper:
                sensor_type = 'CO2'
            elif 'FLAME' in path_upper or 'FLAMA' in path_upper:
                sensor_type = 'FLAME'
            elif 'SMOKE' in path_upper:
                sensor_type = 'SMOKE'
            elif 'TEMP' in path_upper:
                sensor_type = 'TEMPERATURE'
            elif 'H2' in path_upper:
                sensor_type = 'H2'
            elif 'O2' in path_upper:
                sensor_type = 'O2'

            # Extrai nome do sensor
            sensor_name = sensor_path.split('\\')[-1] if '\\' in sensor_path else sensor_path

            sensor_mapping['sensors'].append({
                'path': sensor_path,
                'name': sensor_name,
                'platform': platform,
                'sensor_type': sensor_type,
                'status': 'READY_FOR_IMPORT'
            })

        # Salva arquivo de mapeamento
        output_file = os.path.join(
            project_root,
            'config',
            'sensor_paths_buzios.json'
        )

        with open(output_file, 'w') as f:
            json.dump(sensor_mapping, f, indent=2)

        print(f"✓ Arquivo criado: {output_file}\n")

        # Exibe resumo
        print("="*80)
        print("RESUMO DA DESCOBERTA")
        print("="*80)

        platform_summary = {}
        type_summary = {}

        for sensor in sensor_mapping['sensors']:
            # Por plataforma
            platform = sensor['platform']
            platform_summary[platform] = platform_summary.get(platform, 0) + 1

            # Por tipo
            sensor_type = sensor['sensor_type']
            type_summary[sensor_type] = type_summary.get(sensor_type, 0) + 1

        print("\nSensores por Plataforma:")
        for platform in sorted(platform_summary.keys()):
            count = platform_summary[platform]
            print(f"  {platform}: {count} sensores")

        print("\nSensores por Tipo:")
        for sensor_type in sorted(type_summary.keys()):
            count = type_summary[sensor_type]
            print(f"  {sensor_type}: {count} sensores")

        print(f"\nTotal: {len(sensors)} sensores")
        print("="*80 + "\n")

        print("Próximos passos:")
        print("1. Revise o arquivo: config/sensor_paths_buzios.json")
        print("2. Importe sensores no SafePlan UI (Configuration → Add Sensor)")
        print("3. Ou execute: python scripts/import_sensors_from_af.py")
        print()

        return True

    except Exception as e:
        logger.error(f"Erro em discover_sensors: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = discover_sensors()
    sys.exit(0 if success else 1)
