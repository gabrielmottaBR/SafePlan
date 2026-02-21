"""
Script para descobrir sensores disponíveis no SAURIOPIAF02\DB_BUZIOS_SENSORES
e criar mapeamento para importação no SafePlan.

Estrutura esperada no AF:
  \\SAURIOPIAF02\DB_BUZIOS_SENSORES\Buzios\{UEP}\Sensores\{MODULO}\{MODULO_ZONA}\{MODULO_ZONA_TIPO_GAS}\AST-12236070
  
  Onde:
  - {UEP} = Unidade (P74, P75, P76, P77, P78, P79, FPAB, FPAT, etc)
  - {MODULO} = Módulo (HULL, SEPARATOR, etc)
  - {MODULO_ZONA} = Zona do módulo (HULL_H011, HULL_H012, etc)
  - {MODULO_ZONA_TIPO_GAS} = Tipo de gás (HULL_H011_CH4, HULL_H011_H2S, etc)
  - AST-XXXXX = Atributo específico do sensor

O script navegará recursivamente procurando por essa estrutura e extraindo:
  - UEP como plataforma
  - MODULO_ZONA_TIPO_GAS para identificar tipo de sensor
  - Construirá o path completo

Uso:
    python scripts/discover_sensor_paths.py

Com --demo usa dados de demonstração:
    python scripts/discover_sensor_paths.py --demo

Com --max-results limita número de sensores explorados (padrão: None = todos):
    python scripts/discover_sensor_paths.py --max-results 100
"""
import os
import sys
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional, Set, Tuple

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

# Padrões de tipos de sensores a procurar no final do caminho
SENSOR_TYPE_PATTERNS = {
    'CH4_POINT': ['_CH4', '_METANO'],
    'CH4_PLUME': ['_PLUME'],
    'H2S': ['_H2S', '_SULFETO'],
    'CO2': ['_CO2', '_DIOXIDO'],
    'FLAME': ['_FLAME', '_CHAMA'],
    'SMOKE': ['_SMOKE', '_FUMACA'],
    'TEMPERATURE': ['_TEMP', '_TEMPERAT'],
    'H2': ['_H2', '_HIDROGENIO'],
    'O2': ['_O2', '_OXIGENIO']
}

# Plataformas esperadas
PLATFORMS = ['P74', 'P75', 'P76', 'P77', 'P78', 'P79', 'FPAB', 'FPAT', 'P80', 'P81', 'P82', 'P83']

print("\n" + "="*80)
print("SafePlan - Descoberta de Sensores do PI AF Server")
print("="*80 + "\n")

# Parse args
use_demo = '--demo' in sys.argv
max_results = None
for arg in sys.argv[1:]:
    if arg.startswith('--max-results'):
        if '=' in arg:
            max_results = int(arg.split('=')[1])
        else:
            try:
                idx = sys.argv.index(arg)
                max_results = int(sys.argv[idx + 1])
            except (ValueError, IndexError):
                pass

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
        print("\nProximo passo: python scripts/import_sensors_simple.py")
        print("="*80 + "\n")

    except Exception as e:
        print(f"✗ Erro ao carregar arquivo de demonstração: {e}")
        sys.exit(1)

else:
    print("[1/4] Verificando dependências...")
    try:
        from src.pi_server import gideaoPI
        print("✓ gideaoPI disponível\n")
    except ImportError:
        print("✗ Dependência pythonnet/clr não disponível")
        print("  Tente instalar: pip install pythonnet")
        print(f"  Ou use modo demo: python scripts/discover_sensor_paths.py --demo")
        sys.exit(1)

    class SensorExplorer:
        """Gerencia exploração recursiva da estrutura AF"""
        def __init__(self, max_results: Optional[int] = None):
            self.sensor_list: List[Dict] = []
            self.explored_count = 0
            self.platforms_found: Set[str] = set()
            self.sensor_types_found: Set[str] = set()
            self.max_results = max_results

        def explore(self, db):
            """Inicia exploração a partir de Buzios"""
            try:
                # Navega até Buzios - tenta acessar via Elements
                root_elements = db.Elements
                
                logger.info(f"Exploração iniciada. Elementos encontrados: {root_elements.Count}")
                
                buzios = None
                
                # Procura pelo elemento Buzios
                for elem in root_elements:
                    if elem.Name.upper() == 'BUZIOS':
                        buzios = elem
                        logger.info("Elemento 'Buzios' encontrado")
                        break
                
                if not buzios:
                    logger.warning("Elemento 'Buzios' não encontrado na raiz. Tentando explorar primeiro elemento...")
                    # Se não encontrar Buzios, tenta o primeiro elemento
                    if root_elements.Count > 0:
                        buzios = list(root_elements)[0]
                        logger.info(f"Usando primeiro elemento: {buzios.Name}")
                    else:
                        raise Exception("Nenhum elemento encontrado na raiz da database")
                
                logger.info(f"Iniciando exploração a partir de: {buzios.Name}")
                # Explora plataformas (UEP)
                self._explore_platforms(buzios)
                
            except Exception as e:
                logger.error(f"Erro ao acessar estrutura do AF: {e}")
                raise

        def _explore_platforms(self, buzios_element):
            """Explora plataformas (UEP: P74, P75, etc)"""
            if not hasattr(buzios_element, 'Elements'):
                return

            try:
                uep_elements = list(buzios_element.Elements)
            except Exception as e:
                logger.error(f"Erro ao iterar elementos de plataformas: {e}")
                return

            for uep_element in uep_elements:
                if self.max_results and self.explored_count >= self.max_results:
                    break

                try:
                    uep_name = uep_element.Name.upper()
                    
                    # Verifica se é uma plataforma válida
                    if any(p in uep_name for p in PLATFORMS):
                        logger.debug(f"Encontrada plataforma: {uep_name}")
                        self.platforms_found.add(uep_name)
                        self._explore_sensores_dir(uep_element, uep_name)
                except Exception as e:
                    logger.debug(f"Erro ao explorar plataforma: {e}")
                    continue

        def _explore_sensores_dir(self, uep_element, uep_name: str):
            """Explora diretório 'Sensores' dentro de cada UEP"""
            if not hasattr(uep_element, 'Elements'):
                return

            try:
                sensores_elements = list(uep_element.Elements)
            except Exception as e:
                logger.debug(f"Erro ao iterar elementos de UEP {uep_name}: {e}")
                return

            for elem in sensores_elements:
                if self.max_results and self.explored_count >= self.max_results:
                    break

                try:
                    if elem.Name.upper() == 'SENSORES':
                        logger.debug(f"Encontrado diretório Sensores em {uep_name}")
                        self._explore_modulos(elem, uep_name)
                        break
                except Exception as e:
                    logger.debug(f"Erro ao procurar Sensores: {e}")
                    continue

        def _explore_modulos(self, sensores_element, uep_name: str):
            """Explora módulos (HULL, SEPARATOR, etc)"""
            if not hasattr(sensores_element, 'Elements'):
                return

            try:
                modulo_elements = list(sensores_element.Elements)
            except Exception as e:
                logger.debug(f"Erro ao iterar módulos de {uep_name}: {e}")
                return

            for modulo_element in modulo_elements:
                if self.max_results and self.explored_count >= self.max_results:
                    break

                try:
                    modulo_name = modulo_element.Name.upper()
                    logger.debug(f"Explorando módulo: {modulo_name}")
                    self._explore_modulo_zonas(modulo_element, uep_name, modulo_name)
                except Exception as e:
                    logger.debug(f"Erro ao explorar módulo: {e}")
                    continue

        def _explore_modulo_zonas(self, modulo_element, uep_name: str, modulo_name: str):
            """Explora zonas do módulo (HULL_H011, HULL_H012, etc)"""
            if not hasattr(modulo_element, 'Elements'):
                return

            try:
                zona_elements = list(modulo_element.Elements)
            except Exception as e:
                logger.debug(f"Erro ao iterar zonas de {modulo_name}: {e}")
                return

            for zona_element in zona_elements:
                if self.max_results and self.explored_count >= self.max_results:
                    break

                try:
                    zona_name = zona_element.Name.upper()
                    logger.debug(f"Explorando zona: {zona_name}")
                    self._explore_gas_types(zona_element, uep_name, modulo_name, zona_name)
                except Exception as e:
                    logger.debug(f"Erro ao explorar zona: {e}")
                    continue

        def _explore_gas_types(self, zona_element, uep_name: str, modulo_name: str, zona_name: str):
            """Explora tipos de gás (HULL_H011_CH4, HULL_H011_H2S, etc)"""
            if not hasattr(zona_element, 'Elements'):
                return

            try:
                gas_elements = list(zona_element.Elements)
            except Exception as e:
                logger.debug(f"Erro ao iterar tipos de gás de {zona_name}: {e}")
                return

            for gas_element in gas_elements:
                if self.max_results and self.explored_count >= self.max_results:
                    break

                try:
                    gas_name = gas_element.Name.upper()
                    
                    # Identifica tipo de sensor pelo nome do elemento
                    sensor_type = self._identify_sensor_type(gas_name)
                    
                    if sensor_type:
                        logger.debug(f"Tipo de gás identificado: {sensor_type} ({gas_name})")
                        # Explora atributos deste elemento
                        self._extract_sensor_attributes(
                            gas_element, uep_name, modulo_name, zona_name, gas_name, sensor_type
                        )
                except Exception as e:
                    logger.debug(f"Erro ao explorar tipo de gás: {e}")
                    continue

        def _extract_sensor_attributes(self, gas_element, uep_name: str, modulo_name: str, 
                                       zona_name: str, gas_name: str, sensor_type: str):
            """Extrai sensor tags (AST-XXXX) do elemento tipo de gás"""
            
            try:
                # Primeiro tenta extrair elementos filhos (tags do sensor como subelementos)
                if hasattr(gas_element, 'Elements') and gas_element.Elements.Count > 0:
                    try:
                        sensor_tag_elements = list(gas_element.Elements)
                    except Exception as e:
                        logger.debug(f"Erro ao iterar tags de sensor: {e}")
                        sensor_tag_elements = []
                    
                    for sensor_tag_element in sensor_tag_elements:
                        if self.max_results and self.explored_count >= self.max_results:
                            break

                        try:
                            sensor_tag_name = sensor_tag_element.Name
                            
                            # Construir path completo
                            element_path = f"Buzios\\{uep_name}\\Sensores\\{modulo_name}\\{zona_name}\\{gas_name}\\{sensor_tag_name}"
                            full_path = f"\\\\SAURIOPIAF02\\DB_BUZIOS_SENSORES\\{element_path}"
                            
                            sensor_entry = {
                                'path': full_path,
                                'name': sensor_tag_name,
                                'display_name': f"{sensor_tag_name} - {zona_name}",
                                'platform': uep_name,
                                'sensor_type': sensor_type,
                                'modulo': modulo_name,
                                'zona': zona_name,
                                'gas_type': gas_name,
                                'tag': sensor_tag_name,
                                'element_path': element_path,
                                'status': 'Active'
                            }

                            self.sensor_list.append(sensor_entry)
                            self.explored_count += 1
                            self.sensor_types_found.add(sensor_type)

                            if self.explored_count % 100 == 0:
                                print(f"      ✓ {self.explored_count} sensores encontrados...")
                        except Exception as e:
                            logger.debug(f"Erro ao extrair tag de sensor: {e}")
                            continue

                # Se não há elementos, tenta extrair atributos diretos
                elif hasattr(gas_element, 'Attributes') and gas_element.Attributes.Count > 0:
                    try:
                        attr_list = list(gas_element.Attributes)
                    except Exception as e:
                        logger.debug(f"Erro ao iterar atributos: {e}")
                        attr_list = []
                    
                    for attr in attr_list:
                        if self.max_results and self.explored_count >= self.max_results:
                            break

                        try:
                            attr_name = attr.Name
                            
                            # Construir path completo
                            element_path = f"Buzios\\{uep_name}\\Sensores\\{modulo_name}\\{zona_name}\\{gas_name}"
                            full_path = f"\\\\SAURIOPIAF02\\DB_BUZIOS_SENSORES\\{element_path}\\{attr_name}"
                            
                            sensor_entry = {
                                'path': full_path,
                                'name': attr_name,
                                'display_name': f"{attr_name} - {zona_name}",
                                'platform': uep_name,
                                'sensor_type': sensor_type,
                                'modulo': modulo_name,
                                'zona': zona_name,
                                'gas_type': gas_name,
                                'tag': attr_name,
                                'element_path': element_path,
                                'status': 'Active'
                            }

                            self.sensor_list.append(sensor_entry)
                            self.explored_count += 1
                            self.sensor_types_found.add(sensor_type)

                            if self.explored_count % 100 == 0:
                                print(f"      ✓ {self.explored_count} sensores encontrados...")
                        except Exception as e:
                            logger.debug(f"Erro ao extrair atributo: {e}")
                            continue

            except Exception as e:
                logger.debug(f"Erro em _extract_sensor_attributes: {e}")

        def _identify_sensor_type(self, element_name: str) -> Optional[str]:
            """Identifica tipo de sensor pelo nome do elemento"""
            element_upper = element_name.upper()
            
            for stype, patterns in SENSOR_TYPE_PATTERNS.items():
                for pattern in patterns:
                    if pattern in element_upper:
                        return stype
            
            return None

    try:
        print("[2/4] Conectando a SAURIOPIAF02\\DB_BUZIOS_SENSORES...")
        af_server = gideaoPI.getServidor('SAURIOPIAF02', 'AF')
        if not af_server:
            raise Exception("Falha ao conectar ao AF Server")
        
        db = gideaoPI.getAFDataBase('DB_BUZIOS_SENSORES', af_server)
        if not db:
            raise Exception("Falha ao obter database")
        print("✓ Conectado com sucesso\n")

        print("[3/4] Explorando estrutura com navegação inteligente...")
        print(f"      Estrutura esperada: Buzios\\{{UEP}}\\Sensores\\{{MODULO}}\\{{MODULO_ZONA}}\\{{MODULO_ZONA_TIPO_GAS}}")
        print(f"      (may take several minutes for 5000+ sensors...)\n")

        explorer = SensorExplorer(max_results=max_results)
        explorer.explore(db)

        print(f"✓ Exploração concluída: {explorer.explored_count} sensores encontrados\n")

        # Create mapping
        print("[4/4] Salvando arquivo de mapeamento...")

        sensor_mapping = {
            'discovery_date': datetime.now().isoformat(),
            'af_server': 'SAURIOPIAF02',
            'database': 'DB_BUZIOS_SENSORES',
            'structure': 'Buzios\\{UEP}\\Sensores\\{MODULO}\\{MODULO_ZONA}\\{MODULO_ZONA_TIPO_GAS}',
            'total_sensors': len(explorer.sensor_list),
            'platforms': sorted(list(explorer.platforms_found)),
            'sensor_types': sorted(list(explorer.sensor_types_found)),
            'sensors': explorer.sensor_list
        }

        output_file = os.path.join(project_root, 'config', 'sensor_paths_buzios.json')
        with open(output_file, 'w') as f:
            json.dump(sensor_mapping, f, indent=2)

        print(f"✓ Arquivo salvo em: {output_file}\n")

        # Print summary
        print("="*80)
        print("RESUMO DA DESCOBERTA")
        print("="*80)
        print(f"Total de sensores: {len(explorer.sensor_list)}")
        if explorer.platforms_found:
            print(f"Plataformas encontradas: {', '.join(sorted(explorer.platforms_found))}")
        if explorer.sensor_types_found:
            print(f"Tipos de sensores: {', '.join(sorted(explorer.sensor_types_found))}")
        print("="*80 + "\n")

        if explorer.explored_count > 0:
            print("✓ Descoberta concluída com sucesso!")
            print("\nProximo passo: python scripts/import_sensors_simple.py")
            print("="*80 + "\n")
        else:
            print("⚠ Nenhum sensor encontrado")
            print(f"  Estrutura esperada: \\\\SAURIOPIAF02\\DB_BUZIOS_SENSORES\\Buzios\\{{UEP}}\\Sensores\\...")
            print(f"  Tente: python scripts/discover_sensor_paths.py --demo")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n✗ Operação cancelada pelo usuário")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Erro geral: {e}")
        print(f"✗ Erro: {e}")
        print(f"  Tente: python scripts/discover_sensor_paths.py --demo")
        sys.exit(1)
