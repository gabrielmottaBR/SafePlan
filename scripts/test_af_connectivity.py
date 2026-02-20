"""
Script de diagnóstico para verificar conectividade com PI AF Server.

Uso:
    python scripts/test_af_connectivity.py
"""
import os
import sys
import logging
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

print("\n" + "="*80)
print("SafePlan - PI AF Server Connectivity Test")
print("="*80 + "\n")

print("[1/5] Verificando configuração...")
try:
    from config.settings import Config
    print(f"✓ Config carregada")
    print(f"  - PI Server: {Config.PI_SERVER_HOST}")
except Exception as e:
    print(f"✗ Erro ao carregar config: {e}")
    sys.exit(1)

print("\n[2/5] Verificando arquivo config_gideaopi.json...")
config_file = os.path.join(project_root, 'config', 'config_gideaopi.json')
if os.path.exists(config_file):
    print(f"✓ Arquivo encontrado: {config_file}")
    import json
    with open(config_file, 'r') as f:
        config = json.load(f)
    print(f"  - PI AF SDK path: {config.get('path_pi')}")
    print(f"  - Servidores: {[s['nome'] for s in config.get('servidoresAF', [])]}")
else:
    print(f"✗ Arquivo não encontrado: {config_file}")
    sys.exit(1)

print("\n[3/5] Verificando biblioteca gideaoPI...")
try:
    from src.pi_server import gideaoPI
    print(f"✓ gideaoPI importada com sucesso")
except Exception as e:
    print(f"✗ Erro ao importar gideaoPI: {e}")
    print(f"  Possível solução: Instale PI AF SDK em C:\\Program Files (x86)\\PIPC\\AF\\PublicAssemblies\\4.0")
    sys.exit(1)

print("\n[4/5] Testando conexão com SAURIOPIAF02...")
try:
    af_server = gideaoPI.getServidor('SAURIOPIAF02', 'AF')
    if af_server:
        print(f"✓ Conectado a SAURIOPIAF02")
    else:
        print(f"✗ Falha ao conectar a SAURIOPIAF02")
        sys.exit(1)
except Exception as e:
    print(f"✗ Erro na conexão: {e}")
    print(f"  - Verificar acesso à rede corporativa")
    print(f"  - Verificar se SAURIOPIAF02 está acessível")
    print(f"  - Verificar instalação do PI AF SDK")
    sys.exit(1)

print("\n[5/5] Testando acesso ao banco de dados...")
try:
    db = gideaoPI.getAFDataBase('DB_BUZIOS_SENSORES', af_server)
    if db:
        print(f"✓ Acessado banco: DB_BUZIOS_SENSORES")
    else:
        print(f"✗ Falha ao acessar banco DB_BUZIOS_SENSORES")
        sys.exit(1)
except Exception as e:
    print(f"✗ Erro ao acessar banco: {e}")
    sys.exit(1)

print("\n" + "="*80)
print("✓ TODOS OS TESTES PASSARAM!")
print("="*80)
print("\nProxímo passo: python scripts/discover_sensor_paths.py")
print("="*80 + "\n")
