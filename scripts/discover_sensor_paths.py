"""
Script para descobrir sensores disponíveis no SAURIOPIAF02\DB_BUZIOS_SENSORES
e criar mapeamento para importação no SafePlan.

Uso:
    python scripts/discover_sensor_paths.py [--demo]

Opções:
    --demo  : Usar arquivo de demonstração ao invés de conectar ao AF
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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

print("\n" + "="*80)
print("SafePlan - Descoberta de Sensores do PI AF Server")
print("="*80 + "\n")

# Parse args
use_demo = '--demo' in sys.argv

if use_demo:
    print("MODO DEMO: Usando arquivo de demonstração")
    print("="*80 + "\n")

    # Load demo file
    demo_file = os.path.join(project_root, 'config', 'sensor_paths_buzios_demo.json')

    print("[DEMO] Lendo arquivo de demonstração...")
    try:
        with open(demo_file, 'r') as f:
            sensor_mapping = json.load(f)

        print(f"✓ {sensor_mapping['total_sensors']} sensores de demonstração carregados")

        # Save as real file
        output_file = os.path.join(project_root, 'config', 'sensor_paths_buzios.json')
        with open(output_file, 'w') as f:
            json.dump(sensor_mapping, f, indent=2)

        print(f"✓ Arquivo salvo em: {output_file}")

        # Print summary
        platforms = set()
        sensor_types = set()
        for sensor in sensor_mapping['sensors']:
            platforms.add(sensor['platform'])
            sensor_types.add(sensor['sensor_type'])

        print(f"\nResumo:")
        print(f"  - Plataformas: {', '.join(sorted(platforms))}")
        print(f"  - Tipos: {', '.join(sorted(sensor_types))}")

        print("\n" + "="*80)
        print("✓ Descoberta concluída (modo demo)")
        print("="*80)
        print("\nProximo passo: python scripts/import_sensors_from_af.py")
        print("="*80 + "\n")

    except Exception as e:
        print(f"✗ Erro ao carregar arquivo de demonstração: {e}")
        sys.exit(1)

else:
    print("[1/5] Verificando configuração...")
    try:
        from src.pi_server import gideaoPI
        from src.pi_server.af_manager import AFDatabaseManager
        print("✓ Dependências carregadas")
    except Exception as e:
        print(f"✗ Erro ao carregar dependências: {e}")
        print(f"  Tente: python scripts/discover_sensor_paths.py --demo")
        sys.exit(1)

    try:
        print("\n[2/5] Conectando ao AF Server SAURIOPIAF02...")
        print("      (aguardando conexão...)")

        af_server = gideaoPI.getServidor('SAURIOPIAF02', 'AF')

        if not af_server:
            print("✗ Falha ao conectar ao AF Server")
            print("  Verificar: rede corporativa, acesso a SAURIOPIAF02, PI AF SDK")
            print(f"  Tente: python scripts/discover_sensor_paths.py --demo")
            sys.exit(1)

        print("✓ Conectado com sucesso")

        print("\n[3/5] Obtendo database DB_BUZIOS_SENSORES...")
        print("      (aguardando...)")

        db = gideaoPI.getAFDataBase('DB_BUZIOS_SENSORES', af_server)

        if not db:
            print("✗ Falha ao obter database")
            print(f"  Tente: python scripts/discover_sensor_paths.py --demo")
            sys.exit(1)

        print("✓ Database obtido com sucesso")

        print("\n[4/5] Explorando estrutura da database...")
        print("      (esta etapa pode levar alguns minutos...)")

        manager = AFDatabaseManager(db)
        sensors = manager.get_sensor_paths()

        if not sensors:
            print("⚠ Nenhum sensor encontrado")
            print(f"  Tente: python scripts/discover_sensor_paths.py --demo")
            sys.exit(1)

        print(f"✓ Encontrados {len(sensors)} sensores")

        # Create mapping
        print("\n[5/5] Criando arquivo de mapeamento...")

        sensor_mapping = {
            'discovery_date': datetime.now().isoformat(),
            'af_server': 'SAURIOPIAF02',
            'database': 'DB_BUZIOS_SENSORES',
            'total_sensors': len(sensors),
            'sensors': sensors
        }

        # Save mapping
        output_file = os.path.join(project_root, 'config', 'sensor_paths_buzios.json')
        with open(output_file, 'w') as f:
            json.dump(sensor_mapping, f, indent=2)

        print(f"✓ Arquivo salvo: {output_file}")

        # Print summary
        platforms = set()
        sensor_types = set()
        for sensor in sensors:
            platforms.add(sensor['platform'])
            sensor_types.add(sensor['sensor_type'])

        print(f"\nResumo da Descoberta:")
        print(f"  - Plataformas: {', '.join(sorted(platforms))}")
        print(f"  - Tipos de sensores: {', '.join(sorted(sensor_types))}")

        print("\n" + "="*80)
        print("✓ Descoberta concluída com sucesso!")
        print("="*80)
        print("\nProximo passo: python scripts/import_sensors_from_af.py")
        print("="*80 + "\n")

    except Exception as e:
        print(f"✗ Erro: {e}")
        import traceback
        traceback.print_exc()
        print(f"\n  Tente: python scripts/discover_sensor_paths.py --demo")
        sys.exit(1)
