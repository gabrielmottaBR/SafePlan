"""
AF Database Manager - Exploração da estrutura de sensores no SAURIOPIAF02
Permite descobrir e mapear sensores de fogo/gás no DB_BUZIOS_SENSORES
"""
import logging
from typing import List, Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

# Try to import AF SDK
try:
    import clr
    clr.AddReference("OSIsoft.AFSDK")
    from OSIsoft import AF
    AF_AVAILABLE = True
except Exception as e:
    AF_AVAILABLE = False
    logger.warning(f"AF SDK not available: {e}")


class AFDatabaseManager:
    """
    Gerencia acesso e exploração da database AF do SAURIOPIAF02
    """

    def __init__(self, af_database):
        """
        Inicializa manager com referência do lAF database.

        Args:
            af_database: OSIsoft.AF.AFDatabase do SAURIOPIAF02\DB_BUZIOS_SENSORES
        """
        self.db = af_database
        self.logger = logger

    def list_elements(self, parent_element=None, level=0) -> List[Dict]:
        """
        Lista todos os elementos em uma hierarquia AF.

        Args:
            parent_element: Elemento pai para explorar (None = raiz)
            level: Nível de profundidade

        Returns:
            Lista de dicionários com informações de elementos
        """
        elements_list = []

        try:
            if parent_element is None:
                # Começa da raiz
                elements = self.db.Elements
            else:
                elements = parent_element.Elements

            for element in elements:
                element_info = {
                    'name': element.Name,
                    'type': element.Template.Name if element.Template else 'N/A',
                    'path': element.GetPath(),
                    'level': level,
                    'has_children': element.Elements.Count > 0,
                    'attributes_count': len(element.Attributes) if element.Attributes else 0
                }

                elements_list.append(element_info)

                # Recursão para explorar sub-elementos
                if level < 5:  # Limite de profundidade
                    subelements = self.list_elements(element, level + 1)
                    elements_list.extend(subelements)

            return elements_list

        except Exception as e:
            logger.error(f"Erro ao listar elementos: {e}")
            return []

    def get_sensor_paths(self, platform: str = None) -> List[str]:
        """
        Descobre caminhos de sensores de fogo/gás na database.

        Args:
            platform: Filtra por plataforma (P74, P75, etc.)

        Returns:
            Lista de paths de sensores
        """
        sensor_keywords = [
            'CH4', 'CHANO', 'H2S', 'CO2', 'SMOKE',
            'FLAME', 'FLAMA', 'TEMPERATURE', 'TEMP',
            'H2', 'O2', 'SENSOR', 'DETECTOR'
        ]

        sensor_paths = []

        try:
            elements = self.list_elements()

            for element_info in elements:
                element_name = element_info['name'].upper()

                # Verifica se nome contém keywords de sensor
                if any(kw in element_name for kw in sensor_keywords):
                    # Filtra por plataforma se especificado
                    if platform:
                        if platform.upper() in element_info['path'].upper():
                            sensor_paths.append(element_info['path'])
                    else:
                        sensor_paths.append(element_info['path'])

            logger.info(f"Encontrados {len(sensor_paths)} sensores")
            return sensor_paths

        except Exception as e:
            logger.error(f"Erro ao buscar caminhos de sensores: {e}")
            return []

    def get_element_by_path(self, path: str):
        """
        Obtém elemento AF pelo seu caminho.

        Args:
            path: Caminho completo do elemento

        Returns:
            Objeto AFElement ou None
        """
        try:
            from src.pi_server.gideaoPI import pathToAtributoAF

            # Remove o prefixo do servidor se existir
            if '\\\\' in path:
                path = path.split('|')[0]  # Pega só a parte do elemento

            parts = path.split('\\')
            # Remove partes vazias
            parts = [p for p in parts if p]

            # Navega pela hierarquia
            element = self.db.Elements.get_Item(parts[-1]) if parts else None

            return element

        except Exception as e:
            logger.error(f"Erro ao obter elemento {path}: {e}")
            return None

    def explore_structure(self, max_levels=4) -> Dict:
        """
        Explora e retorna a estrutura completa da database.

        Args:
            max_levels: Profundidade máxima a explorar

        Returns:
            Dicionário com estrutura da database
        """
        structure = {
            'database_name': self.db.Name,
            'database_path': self.db.GetPath(),
            'elements_count': self.db.Elements.Count,
            'root_elements': [],
            'platforms': {},
            'sensor_summary': {}
        }

        try:
            # Lista elementos raiz
            for element in self.db.Elements:
                element_info = {
                    'name': element.Name,
                    'path': element.GetPath(),
                    'element_count': element.Elements.Count,
                    'sub_elements': []
                }

                # Explora um nível abaixo
                for sub_element in element.Elements:
                    sub_info = {
                        'name': sub_element.Name,
                        'path': sub_element.GetPath()
                    }
                    element_info['sub_elements'].append(sub_info)

                    # Organiza por plataforma
                    platform = element.Name
                    if platform not in structure['platforms']:
                        structure['platforms'][platform] = []

                    structure['platforms'][platform].append(sub_element.Name)

                structure['root_elements'].append(element_info)

            # Contar sensores por tipo
            all_paths = self.get_sensor_paths()
            for path in all_paths:
                # Extrai tipo de sensor do caminho
                path_upper = path.upper()
                if 'CH4' in path_upper:
                    sensor_type = 'CH4'
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
                else:
                    sensor_type = 'OTHER'

                if sensor_type not in structure['sensor_summary']:
                    structure['sensor_summary'][sensor_type] = 0

                structure['sensor_summary'][sensor_type] += 1

            return structure

        except Exception as e:
            logger.error(f"Erro ao explorar estrutura: {e}")
            return structure

    def print_structure(self):
        """Printa estrutura da database de forma legível"""
        try:
            structure = self.explore_structure()

            print("\n" + "="*70)
            print(f"DATABASE: {structure['database_name']}")
            print(f"PATH: {structure['database_path']}")
            print(f"ROOT ELEMENTS: {structure['elements_count']}")
            print("="*70)

            print("\nPlatformas encontradas:")
            for platform, sensors in structure['platforms'].items():
                print(f"  • {platform}: {len(sensors)} elementos")

            print("\nResumo de sensores por tipo:")
            for sensor_type, count in structure['sensor_summary'].items():
                print(f"  • {sensor_type}: {count} sensores")

            print("\nElementos raiz:")
            for element in structure['root_elements']:
                print(f"  • {element['name']}")
                print(f"    Path: {element['path']}")
                print(f"    Sub-elementos: {element['element_count']}")
                if element['sub_elements'][:3]:  # Mostra os 3 primeiros
                    for sub in element['sub_elements'][:3]:
                        print(f"      - {sub['name']}")
                    if len(element['sub_elements']) > 3:
                        print(f"      ... e mais {len(element['sub_elements']) - 3}")

            print("\n" + "="*70 + "\n")

        except Exception as e:
            logger.error(f"Erro ao imprimir estrutura: {e}")


def discover_af_database():
    """
    Script para descobrir estrutura do SAURIOPIAF02\\DB_BUZIOS_SENSORES
    """
    try:
        from src.pi_server import gideaoPI

        logger.info("Conectando ao AF Server SAURIOPIAF02...")
        af_server = gideaoPI.getServidor('SAURIOPIAF02', 'AF')

        if not af_server:
            logger.error("Falha ao conectar ao AF Server")
            return False

        logger.info("Obtendo database DB_BUZIOS_SENSORES...")
        db = gideaoPI.getAFDataBase('DB_BUZIOS_SENSORES', af_server)

        if not db:
            logger.error("Falha ao obter database")
            return False

        # Explora estrutura
        manager = AFDatabaseManager(db)
        manager.print_structure()

        # Busca sensores
        logger.info("\nBuscando sensores...")
        sensors = manager.get_sensor_paths()

        print(f"\nTotal de sensores encontrados: {len(sensors)}")
        print("\nPrimeiros 10 sensores:")
        for i, sensor_path in enumerate(sensors[:10]):
            print(f"  {i+1}. {sensor_path}")

        return True
    
    except Exception as e:
        logger.error(f"Error discovering AF database: {e}")
        return False


class AFManager:
    """
    High-level AF Server connection manager.
    
    Provides connection to PI AF Server and methods to retrieve sensor data.
    """
    
    DEFAULT_AF_SERVER = "SAURIOPIAF02"
    DEFAULT_AF_DATABASE = "DB_BUZIOS_SENSORES"
    
    def __init__(self, af_server: str = None, af_database: str = None):
        """
        Initialize AF Server connection.
        
        Args:
            af_server: AF Server name (default: SAURIOPIAF02)
            af_database: AF Database name (default: DB_BUZIOS_SENSORES)
        """
        self.af_server_name = af_server or self.DEFAULT_AF_SERVER
        self.af_database_name = af_database or self.DEFAULT_AF_DATABASE
        self.af_system = None
        self.af_database = None
        self.manager = None
        
        if not AF_AVAILABLE:
            raise RuntimeError("AF SDK not available. Install pythonnet and AF SDK.")
        
        self._connect()
    
    def _connect(self):
        """Connect to AF Server and get database reference."""
        try:
            logger.info(f"Connecting to AF Server: {self.af_server_name}...")
            self.af_system = AF.PISystems()[self.af_server_name]
            
            logger.info(f"Connected. Getting database: {self.af_database_name}...")
            self.af_database = self.af_system.Databases[self.af_database_name]
            
            self.manager = AFDatabaseManager(self.af_database)
            logger.info(f"✓ AF Database connected successfully")
        
        except Exception as e:
            logger.error(f"Error connecting to AF Server: {e}")
            raise
    
    def get_element_by_path(self, path: str) -> Optional[object]:
        """
        Get AF element by its path string.
        
        Args:
            path: Full path string (e.g., "Buzios\\P74\\...")
            
        Returns:
            AF Element object or None if not found
        """
        if not self.af_database:
            return None
        
        try:
            # Replace forward slashes with backslashes
            path = path.replace("/", "\\")
            
            # Split path and navigate
            parts = path.split("\\")
            current_element = None
            
            for part in parts:
                if not part:
                    continue
                
                if current_element is None:
                    # Root level
                    if part in [elem.Name for elem in self.af_database.Elements]:
                        current_element = self.af_database.Elements[part]
                    else:
                        return None
                else:
                    # Navigate deeper
                    if part in [elem.Name for elem in current_element.Elements]:
                        current_element = current_element.Elements[part]
                    else:
                        return None
            
            return current_element
        
        except Exception as e:
            logger.debug(f"Error navigating path {path}: {e}")
            return None
    
    def get_element_attributes(self, element: object) -> Dict[str, object]:
        """
        Get attributes from AF element.
        
        Args:
            element: AF Element object
            
        Returns:
            Dict mapping attribute names to values
        """
        if not element:
            return {}
        
        attributes = {}
        try:
            if hasattr(element, 'Attributes'):
                for attr in element.Attributes:
                    try:
                        value = attr.GetValue() if hasattr(attr, 'GetValue') else attr.Value
                        attributes[attr.Name] = value
                    except Exception as e:
                        logger.debug(f"Error getting attribute {attr.Name}: {e}")
        
        except Exception as e:
            logger.debug(f"Error getting attributes: {e}")
        
        return attributes
    
    def discover_sensors_by_path(self, paths: List[str]) -> List[Dict[str, object]]:
        """
        Discover sensors given a list of paths.
        
        Args:
            paths: List of AF element paths
            
        Returns:
            List of sensor dicts with extracted attributes
        """
        sensors = []
        for path in paths:
            try:
                element = self.get_element_by_path(path)
                if element:
                    attributes = self.get_element_attributes(element)
                    attributes['path_af'] = path
                    sensors.append(attributes)
            except Exception as e:
                logger.debug(f"Error discovering sensor at {path}: {e}")
        
        return sensors


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    discover_af_database()
