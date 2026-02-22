"""
Script para importar sensores do arquivo sensor_paths_buzios.json 
gerado por discover_sensors_from_af.py para o banco de dados SafePlan.

Uso:
    python scripts/import_sensors_from_buzios.py [--dry-run]
"""
import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import Config
from src.data.database import DatabaseManager, init_database
from src.sensors.sensor_manager import create_sensor_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Default thresholds by gas type
DEFAULT_THRESHOLDS = {
    'CH4': {'lower_ok': 0, 'lower_warning': 5, 'upper_warning': 50, 'upper_critical': 100, 'unit': 'ppm'},
    'H2S': {'lower_ok': 0, 'lower_warning': 1, 'upper_warning': 10, 'upper_critical': 20, 'unit': 'ppm'},
    'CO2': {'lower_ok': 0, 'lower_warning': 100, 'upper_warning': 5000, 'upper_critical': 10000, 'unit': 'ppm'},
    'H2': {'lower_ok': 0, 'lower_warning': 10, 'upper_warning': 100, 'upper_critical': 500, 'unit': 'ppm'},
    'FLAME': {'lower_ok': 0, 'lower_warning': 1, 'upper_warning': 2, 'upper_critical': 3, 'unit': 'level'},
    'O2': {'lower_ok': 19, 'lower_warning': 18, 'upper_warning': 22, 'upper_critical': 25, 'unit': '%'},
    'SMOKE': {'lower_ok': 0, 'lower_warning': 10, 'upper_warning': 50, 'upper_critical': 100, 'unit': 'obscuration %'},
}


def load_sensors_json():
    """Load discovered sensors from JSON file."""
    json_file = project_root / 'config' / 'sensor_paths_buzios.json'
    if not json_file.exists():
        logger.error(f"Arquivo nao encontrado: {json_file}")
        return None
    logger.info(f"Carregando sensores de: {json_file}")
    with open(json_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_sensor_type(tipo_gas: str) -> str:
    """Map gas type to sensor type."""
    tipo_gas_upper = str(tipo_gas).upper() if tipo_gas else 'N/A'
    mapping = {
        'CH4': 'GAS_DETECTOR', 'H2S': 'GAS_DETECTOR', 'CO2': 'GAS_DETECTOR',
        'H2': 'GAS_DETECTOR', 'FLAME': 'FLAME_DETECTOR', 'O2': 'GAS_DETECTOR',
        'SMOKE': 'SMOKE_DETECTOR',
    }
    return mapping.get(tipo_gas_upper, 'GAS_DETECTOR')


def import_sensors(dry_run=False):
    """Import sensors from JSON to database."""
    print("\n" + "="*80)
    print("SafePlan - Importacao de Sensores (BUZIOS - 9,983 sensores)")
    print("="*80 + "\n")
    
    try:
        # Load discovered sensors
        print("[1/4] Carregando sensores descobertos...")
        data = load_sensors_json()
        if not data:
            return False
        
        metadata = data.get('metadata', {})
        sensors_list = data.get('sensors', [])
        
        print(f"[OK] {len(sensors_list)} sensores carregados")
        print(f"  Servidor: {metadata.get('af_server', 'N/A')}")
        print(f"  Banco: {metadata.get('af_database', 'N/A')}")
        plat_list = ', '.join(sorted(metadata.get('platforms', [])))
        print(f"  Plataformas: {len(metadata.get('platforms', []))} = {plat_list}")
        
        if dry_run:
            print("\n[DRY-RUN] Simulacao: o que seria importado...\n")
            return dry_run_import(sensors_list)
        
        # Initialize database
        print("\n[2/4] Inicializando banco de dados...")
        init_database(Config.DATABASE_URL)
        db = DatabaseManager(Config.DATABASE_URL)
        print("[OK] Banco inicializado\n")
        
        # Create sensor manager
        print("[3/4] Preparando para importacao...")
        sensor_mgr = create_sensor_manager()
        print(f"[OK] Sensor manager ativo\n")
        
        # Import sensors
        print("[4/4] Importando sensores...")
        print("-" * 80)
        
        imported_count = 0
        skipped_count = 0
        
        for idx, sensor_data in enumerate(sensors_list, 1):
            try:
                # Extract sensor information
                sensor_id_af = sensor_data.get('id_af', f'SENSOR_{idx}')
                descricao = sensor_data.get('descricao', 'N/A')
                fabricante = sensor_data.get('fabricante', 'N/A')
                tipo_gas = sensor_data.get('tipo_gas', 'N/A')
                tipo_leitura = sensor_data.get('tipo_leitura', 'N/A')
                grupo = sensor_data.get('grupo') or 'N/A'
                modulo = sensor_data.get('modulo')  # Novo: lê de coluna D da planilha
                uep = sensor_data.get('uep', 'UNKNOWN')
                valor_ma = sensor_data.get('valor_ma')
                valor_pct = sensor_data.get('valor_pct')
                path_af = sensor_data.get('path_af', '')
                
                # Derive sensor type
                sensor_type = get_sensor_type(tipo_gas)
                
                # Build names
                internal_name = f"{uep}_{sensor_id_af}"[:100]
                display_name = f"{descricao} ({grupo}/{uep})"[:100] if descricao != 'N/A' else f"{sensor_id_af} ({tipo_gas}/{uep})"[:100]
                
                # Get thresholds
                thresholds = DEFAULT_THRESHOLDS.get(tipo_gas, DEFAULT_THRESHOLDS.get('CH4'))
                unit = thresholds.get('unit', 'ppm')
                
                # Create sensor
                sensor = sensor_mgr.create_sensor(
                    internal_name=internal_name,
                    display_name=display_name,
                    sensor_type=sensor_type,
                    platform=uep,
                    unit=unit,
                    pi_server_tag=path_af,
                    lower_ok_limit=thresholds['lower_ok'],
                    lower_warning_limit=thresholds['lower_warning'],
                    upper_warning_limit=thresholds['upper_warning'],
                    upper_critical_limit=thresholds['upper_critical'],
                    id_af=sensor_id_af,
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
                
                if sensor:
                    if idx <= 5 or idx % 500 == 0 or idx == len(sensors_list):
                        print(f"[OK] [{idx:5}/{len(sensors_list):5}] {sensor_id_af:25} | {tipo_gas:6} | {uep:6}")
                    imported_count += 1
                    
                    # Create alert rules
                    try:
                        sensor_mgr.create_alert_rule(sensor.sensor_id, 'THRESHOLD', 3, thresholds['upper_warning'])
                        sensor_mgr.create_alert_rule(sensor.sensor_id, 'THRESHOLD', 4, thresholds['upper_critical'])
                    except:
                        pass
                else:
                    skipped_count += 1
                    
            except Exception as e:
                skipped_count += 1
                if idx <= 5:
                    print(f"[ERR] [{idx:5}/{len(sensors_list):5}] Erro: {str(e)[:50]}")
        
        print("-" * 80 + "\n")
        print("="*80)
        print("RESUMO DA IMPORTACAO")
        print("="*80)
        print(f"Total processado:           {len(sensors_list):6}")
        print(f"[OK] Importados:            {imported_count:6}")
        print(f"[SKIP] Erros:               {skipped_count:6}")
        print("="*80 + "\n")
        
        if imported_count > 0:
            print(f"[SUCCESS] {imported_count} sensores importados com sucesso!")
            print("\nProximos passos:")
            print("1. Dashboard: streamlit run app/main.py")
            print("2. Verificar sensores: Configuration --> List Sensors")
            print("3. Treinar modelos: Predictions --> Training")
            return True
        else:
            print("[FAILED] Nenhum sensor foi importado")
            return False
            
    except Exception as e:
        logger.error(f"Erro fatal: {e}", exc_info=True)
        return False


def dry_run_import(sensors_list):
    """Show what would be imported."""
    print(f"Total a importar: {len(sensors_list)} sensores\n")
    print("AMOSTRA (primeiros 5):")
    print("-" * 80)
    
    for idx, s in enumerate(sensors_list[:5], 1):
        print(f"\n[{idx}] ID: {s.get('id_af', 'N/A')}")
        print(f"    Gas: {s.get('tipo_gas', 'N/A')}")
        print(f"    Platform: {s.get('uep', 'UNKNOWN')}")
        print(f"    Path: {s.get('path_af', '')[:80]}")
    
    # Statistics
    print("\n" + "="*80)
    print("ESTATISTICAS")
    print("="*80)
    
    platforms = {}
    gas_types = {}
    for s in sensors_list:
        uep = s.get('uep', 'UNKNOWN')
        gas = s.get('tipo_gas', 'N/A')
        platforms[uep] = platforms.get(uep, 0) + 1
        gas_types[gas] = gas_types.get(gas, 0) + 1
    
    print(f"\nPlataformas ({len(platforms)}):")
    for p in sorted(platforms.keys()):
        print(f"  {p:10}: {platforms[p]:5} sensores")
    
    print(f"\nTipos de Gas ({len(gas_types)}):")
    for g in sorted(gas_types.keys()):
        print(f"  {g:10}: {gas_types[g]:5} sensores")
    
    print("\n[OK] Simulacao concluida. Use sem --dry-run para importar.")
    return True


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Import discovered sensors to SafePlan')
    parser.add_argument('--dry-run', action='store_true', help='Simulate import without saving')
    args = parser.parse_args()
    
    try:
        success = import_sensors(dry_run=args.dry_run)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n[CANCELLED] Importacao cancelada")
        sys.exit(1)
