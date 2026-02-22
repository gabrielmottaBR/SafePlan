#!/usr/bin/env python3
"""
Discover sensors from PI AF using paths from Sensores.xlsx (9,983 sensors).

This script reads sensor paths from Excel and builds complete AF paths with
server and database information. It then extracts 10 required attributes.

Example complete path:
    \\SAURIOPIAF02\DB_BUZIOS_SENSORES\Buzios\P74\Sensores\HULL\...\SENSOR_ID|VALOR_PCT

This script:
1. Reads sensor paths from Excel file exported from PI Builder
2. Builds complete AF paths with \\SAURIOPIAF02\DB_BUZIOS_SENSORES prefix
3. Connects to PI AF Server (SAURIOPIAF02\DB_BUZIOS_SENSORES)
4. For each path, navigates to the element and extracts attributes:
   - ID: Unique sensor identifier
   - Descricao: Description
   - Fabricante: Manufacturer
   - Tipo: Type
   - TIPO_GAS: Gas type (CH4, H2S, CO2, FLAME, SMOKE, etc)
   - TIPO_LEITURA: Reading type
   - Grupo: Voting group (for bypass/override degradation detection)
   - UEP: Platform/Unit (P74-P80, FPAB, FPAT, etc)
   - VALOR_mA: Current mA reading
   - VALOR_PCT: Percentage conversion of mA

Usage:
    # Real mode (connects to PI AF Server)
    python scripts/discover_sensors_from_af.py
    
    # Demo mode (uses sample data, no AF connection needed)
    python scripts/discover_sensors_from_af.py --demo
    
    # Limit to first N sensors
    python scripts/discover_sensors_from_af.py --max-results=500
    
    # Verbose output
    python scripts/discover_sensors_from_af.py --verbose
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import logging
from collections import defaultdict

# Try pandas for Excel reading
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from src.pi_server.af_manager import AFManager
    AF_AVAILABLE = True
except Exception as e:
    logger.warning(f"AFManager not available: {e}")
    AF_AVAILABLE = False


class SensorDiscoveryFromAF:
    """
    Discovers sensors from PI AF Server using paths from Excel export.
    
    The Excel file (Sensores.xlsx) is exported from PI Builder with 9,983 sensor paths.
    This class reads those paths and navigates the AF Server to extract attributes.
    
    Complete AF path format:
        \\SAURIOPIAF02\DB_BUZIOS_SENSORES\Buzios\P74\Sensores\...\SENSOR_ID
    
    Attributes extracted from each sensor element via AF SDK or path analysis:
    - id_af: Unique sensor ID (TAG)
    - descricao: Description from PI AF
    - fabricante: Manufacturer attribute
    - tipo: Sensor type
    - tipo_gas: Gas type being detected (CH4, H2S, CO2, FLAME, SMOKE, etc)
    - tipo_leitura: Reading measurement type
    - grupo: Voting group (for bypass/override degradation detection)
    - uep: Platform/Unit where sensor installed (P74-P80, FPAB, FPAT, etc)
    - valor_ma: Current reading in milliamps
    - valor_pct: Reading converted to percentage
    """
    
    # PI AF Server connection details
    AF_SERVER = "SAURIOPIAF02"
    AF_DATABASE = "DB_BUZIOS_SENSORES"
    AF_PATH_PREFIX = f"\\\\{AF_SERVER}\\{AF_DATABASE}\\"
    
    # Attributes to extract from AF elements
    REQUIRED_ATTRIBUTES = [
        'ID', 'Descricao', 'FABRICANTE', 'Tipo', 'TIPO_GAS',
        'TIPO_LEITURA', 'Grupo', 'UEP', 'VALOR_mA', 'VALOR_PCT'
    ]
    
    # Map AF attribute names to our field names
    ATTRIBUTE_MAPPING = {
        'ID': 'id_af',
        'Descricao': 'descricao',
        'FABRICANTE': 'fabricante',
        'Tipo': 'tipo',
        'TIPO_GAS': 'tipo_gas',
        'TIPO_LEITURA': 'tipo_leitura',
        'Grupo': 'grupo',
        'UEP': 'uep',
        'VALOR_mA': 'valor_ma',
        'VALOR_PCT': 'valor_pct',
    }
    
    DEMO_SENSORS_COUNT = 20  # Demo mode: sample 20 sensors
    
    def __init__(self, demo_mode: bool = False, max_results: Optional[int] = None,
                 verbose: bool = False):
        """
        Initialize sensor discovery.
        
        Args:
            demo_mode: Use demo data instead of real AF connection
            max_results: Limit number of sensors to process
            verbose: Enable verbose logging
        """
        self.demo_mode = demo_mode
        self.max_results = max_results
        self.verbose = verbose
        
        self.sensors_found = 0
        self.sensors_errors = 0
        self.sensors_skipped = 0
        self.excel_file = PROJECT_ROOT / 'docs' / 'Sensores.xlsx'
        
        if verbose:
            logging.getLogger().setLevel(logging.DEBUG)
        
        # Initialize AF Manager if available and not in demo mode
        self.af_manager = None
        if AF_AVAILABLE and not demo_mode:
            try:
                logger.info(f"Initializing PI AF Server connection ({self.AF_SERVER}\\{self.AF_DATABASE})...")
                self.af_manager = AFManager(self.AF_SERVER, self.AF_DATABASE)
                logger.info("✓ PI AF Server connected")
            except Exception as e:
                logger.warning(f"Could not connect to PI AF Server: {e}")
                logger.info("Falling back to path-based discovery (attributes may be limited)")
    
    def read_excel_paths(self) -> List[str]:
        """
        Read sensor paths from Excel file.
        
        Returns:
            List of AF element paths (relative, without SAURIOPIAF02 prefix)
        """
        if not self.excel_file.exists():
            logger.error(f"Excel file not found: {self.excel_file}")
            return []
        
        logger.info(f"Reading sensor paths from: {self.excel_file}")
        
        try:
            if not PANDAS_AVAILABLE:
                logger.error("pandas required. Install with: pip install pandas")
                return []
            
            df = pd.read_excel(self.excel_file, sheet_name='SENSORES')
            paths = df['PATH'].tolist()
            
            logger.info(f"✓ Read {len(paths)} sensor paths from Excel")
            
            # Limit if specified
            if self.max_results:
                paths = paths[:self.max_results]
                logger.info(f"  Limited to {len(paths)} sensors (--max-results={self.max_results})")
            
            # Demo mode: use sample
            if self.demo_mode:
                paths = paths[:self.DEMO_SENSORS_COUNT]
                logger.info(f"  Demo mode: using first {len(paths)} sensors")
            
            return paths
            
        except Exception as e:
            logger.error(f"Error reading Excel: {e}")
            return []
    
    def build_complete_path(self, relative_path: str) -> str:
        """
        Build complete AF path with server and database.
        
        Args:
            relative_path: Path without SAURIOPIAF02 prefix
                          (e.g., "Buzios\\P74\\Sensores\\...")
            
        Returns:
            Complete path (e.g., "\\SAURIOPIAF02\DB_BUZIOS_SENSORES\Buzios\...")
        """
        if not relative_path:
            return self.AF_PATH_PREFIX
        
        # Normalize path separators
        relative_path = relative_path.replace('/', '\\')
        
        # Ensure no duplicate prefixes
        if relative_path.startswith(self.AF_PATH_PREFIX):
            return relative_path
        if relative_path.startswith('\\\\'):
            return relative_path
        
        return self.AF_PATH_PREFIX + relative_path
    
    def navigate_element_path(self, path: str) -> Optional[Any]:
        """
        Navigate PI AF to find element at given path.
        
        Args:
            path: Complete AF path (e.g., "\\SAURIOPIAF02\DB_BUZIOS_SENSORES\Buzios\...")
            
        Returns:
            AF Element object or None if not found
        """
        if not self.af_manager:
            return None
        
        try:
            # Remove AF_PATH_PREFIX for AF navigation
            relative_path = path.replace(self.AF_PATH_PREFIX, '')
            return self.af_manager.get_element_by_path(relative_path)
        except Exception as e:
            if self.verbose:
                logger.debug(f"Error navigating to {path}: {e}")
            return None
    
    def extract_attributes_from_af(self, element: Any, path: str) -> Dict[str, Any]:
        """
        Extract attributes from AF element.
        
        Args:
            element: AF Element object
            path: Full AF path
            
        Returns:
            Dict with extracted attributes
        """
        attributes = {'path_af': path}
        
        if not element:
            return attributes
        
        try:
            # Extract each required attribute
            for af_attr_name, field_name in self.ATTRIBUTE_MAPPING.items():
                try:
                    # Try to get attribute from element
                    value = None
                    
                    # Try different ways to access attributes
                    if hasattr(element, 'Attributes'):
                        # If element has Attributes collection
                        if af_attr_name in element.Attributes:
                            attr_obj = element.Attributes[af_attr_name]
                            if hasattr(attr_obj, 'GetValue'):
                                value = attr_obj.GetValue()
                            else:
                                value = attr_obj.Value if hasattr(attr_obj, 'Value') else str(attr_obj)
                    elif hasattr(element, af_attr_name):
                        # Direct attribute access
                        value = getattr(element, af_attr_name)
                    
                    if value is not None:
                        attributes[field_name] = value
                
                except Exception as e:
                    if self.verbose:
                        logger.debug(f"Error extracting {af_attr_name}: {e}")
        
        except Exception as e:
            logger.error(f"Error extracting attributes from element: {e}")
        
        # Fallback: fill missing attributes from path analysis
        fallback_attrs = self.extract_attributes_from_path(path)
        for key, value in fallback_attrs.items():
            if key not in attributes or attributes[key] is None:
                attributes[key] = value
        
        return attributes
    
    def extract_attributes_from_path(self, path: str) -> Dict[str, Any]:
        """
        Extract attributes by analyzing the path structure.
        
        AF paths follow patterns like:
        \\SAURIOPIAF02\DB_BUZIOS_SENSORES\Buzios\P74\Sensores\HULL\HULL_FT_5252801\HULL_FT_5252801_CH4\AST-A110001
        
        This extracts information from the path structure as fallback.
        
        Args:
            path: Full AF path (with SAURIOPIAF02 prefix)
            
        Returns:
            Dict with extracted attributes (partial, based on path analysis)
        """
        # Ensure path has complete AF prefix
        if not path.startswith(self.AF_PATH_PREFIX):
            path = self.build_complete_path(path)
        
        attributes = {'path_af': path}  # Always save complete path with prefix
        
        if not path:
            return attributes
        
        # Remove prefix for parsing
        parse_path = path.replace(self.AF_PATH_PREFIX, '')
        parts = parse_path.split('\\')
        
        # Extract platform from path (usually at position 1: "Buzios\P74\...")
        for i, part in enumerate(parts):
            if part.startswith('P') and len(part) <= 3 and part[1:].isdigit():
                attributes['uep'] = part
                break
            elif part in ['FPAB', 'FPAT']:
                attributes['uep'] = part
                break
        
        # Extract sensor ID (usually in the last few parts)
        if len(parts) >= 2:
            # Special handling for FPAT: use last two parts to ensure uniqueness
            # (e.g., "CH4-Main Deck" + "553-GIR-2851" → "CH4-Main Deck_553-GIR-2851")
            if attributes.get('uep') == 'FPAT' and len(parts) >= 2:
                last_part = parts[-1] if parts[-1] else None
                second_last_part = parts[-2] if len(parts) >= 2 else None
                if last_part and second_last_part and '-' in last_part:
                    # Combine for uniqueness: "CH4-Main Deck_553-GIR-2851"
                    attributes['id_af'] = f"{second_last_part}_{last_part}"
                elif last_part and '-' in last_part:
                    attributes['id_af'] = last_part
            else:
                # Try last non-empty part that looks like a sensor ID for other platforms
                for part in reversed(parts):
                    # Sensor IDs often start with letters: AST-, FD-, O2-, etc
                    if part and '-' in part and any(c.isalpha() for c in part[:3]):
                        attributes['id_af'] = part
                        break
        
        # Try to detect gas type from path
        path_lower = path.lower()
        if 'ch4' in path_lower or '_ch4' in path_lower:
            attributes['tipo_gas'] = 'CH4'
        elif 'h2s' in path_lower or '_h2s' in path_lower:
            attributes['tipo_gas'] = 'H2S'
        elif 'co2' in path_lower or '_co2' in path_lower:
            attributes['tipo_gas'] = 'CO2'
        elif 'fd' in path_lower or '_fd' in path_lower or 'flame' in path_lower:
            attributes['tipo_gas'] = 'FLAME'
        elif 'o2' in path_lower or '_o2' in path_lower:
            attributes['tipo_gas'] = 'O2'
        elif 'h2' in path_lower or '_h2' in path_lower:
            attributes['tipo_gas'] = 'H2'
        
        # Try to detect reading type (TIPO_LEITURA) from path
        # Look for common patterns: %, ppm, PCT, C, LEVEL, obscuration, etc.
        if '%' in path_lower or 'pct' in path_lower:
            attributes['tipo_leitura'] = '%'
        elif 'ppm' in path_lower:
            attributes['tipo_leitura'] = 'ppm'
        elif 'level' in path_lower:
            attributes['tipo_leitura'] = 'LEVEL'
        elif 'obscuration' in path_lower or 'smoke' in path_lower:
            attributes['tipo_leitura'] = 'obscuration %'
        elif 'celsius' in path_lower or 'temperature' in path_lower or '_c' in path_lower:
            attributes['tipo_leitura'] = 'C'
        # If still not set and we have gas type, try to infer from gas type
        elif 'tipo_leitura' not in attributes and 'tipo_gas' in attributes:
            gas_type = attributes['tipo_gas'].upper()
            if gas_type in ['CH4', 'H2S', 'CO2', 'H2']:
                attributes['tipo_leitura'] = 'ppm'
            elif gas_type == 'O2':
                attributes['tipo_leitura'] = '%'
            elif gas_type == 'FLAME':
                attributes['tipo_leitura'] = 'LEVEL'
            elif gas_type == 'SMOKE':
                attributes['tipo_leitura'] = 'obscuration %'
        
        # Extract grupo (voting group) from path if visible
        # Usually some elements are grouped: e.g., HULL_FT_5252801
        if len(parts) >= 3:
            # Try to find a pattern like HULL, SEPARATOR, COMPRESSOR
            for part in parts:
                if any(keyword in part.upper() for keyword in ['HULL', 'SEPARATOR', 'COMPRESSOR', 'PROCESSAMENTO']):
                    attributes['grupo'] = part
                    break
        
        return attributes
    
    def discover_sensors(self) -> List[Dict[str, Any]]:
        """
        Discover all sensors using Excel paths and AF attributes.
        
        Returns:
            List of sensor dicts with all extracted attributes
        """
        logger.info("="*80)
        logger.info("SENSOR DISCOVERY FROM PI AF SERVER")
        logger.info(f"Source: Excel(Sensores.xlsx) + PI AF({self.AF_SERVER}\\{self.AF_DATABASE})")
        logger.info(f"Mode: {'DEMO' if self.demo_mode else 'REAL'}")
        if self.max_results:
            logger.info(f"Limit: {self.max_results} sensors")
        logger.info("="*80)
        
        # Read paths from Excel
        paths = self.read_excel_paths()
        if not paths:
            logger.error("No paths read from Excel")
            return []
        
        logger.info(f"\nProcessing {len(paths)} sensor paths...")
        logger.info("="*80 + "\n")
        
        sensors = []
        for idx, relative_path in enumerate(paths, 1):
            try:
                # Build complete AF path
                complete_path = self.build_complete_path(relative_path)
                
                # Debug: log first 3 paths
                if idx <= 3:
                    logger.info(f"DEBUG [{idx}] relative_path: {relative_path[:50]}...")
                    logger.info(f"DEBUG [{idx}] complete_path: {complete_path[:80]}...")
                
                # Try to get attributes from AF Server first
                element = self.navigate_element_path(complete_path) if self.af_manager else None
                
                if element:
                    # Extract from AF
                    attributes = self.extract_attributes_from_af(element, complete_path)
                else:
                    # Fallback: extract from path structure
                    attributes = self.extract_attributes_from_path(complete_path)
                
                # Debug: log first 3 path_af values
                if idx <= 3:
                    logger.info(f"DEBUG [{idx}] saved path_af: {attributes.get('path_af', 'NONE')[:80]}...")
                
                # Validate: must have at least ID or path
                if attributes.get('id_af') or attributes.get('path_af'):
                    sensors.append(attributes)
                    self.sensors_found += 1
                    
                    # Log progress
                    if idx % max(1, len(paths) // 20) == 0 or self.demo_mode or idx <= 5:
                        id_af = attributes.get('id_af', 'UNKNOWN')
                        tipo_gas = attributes.get('tipo_gas', 'N/A')
                        uep = attributes.get('uep', 'UNKNOWN')
                        logger.info(f"  [{idx:5}/{len(paths):5}] {id_af:20} | "
                                  f"{str(tipo_gas):10} | {uep}")
                else:
                    self.sensors_skipped += 1
                
            except Exception as e:
                self.sensors_errors += 1
                if self.verbose:
                    logger.error(f"Error processing path {idx}: {e}")
                continue
        
        logger.info("\n" + "="*80)
        logger.info(f"✓ Found {self.sensors_found} sensors")
        if self.sensors_skipped:
            logger.warning(f"⚠ Skipped {self.sensors_skipped} invalid sensors")
        if self.sensors_errors:
            logger.warning(f"⚠ {self.sensors_errors} errors during processing")
        logger.info("="*80)
        
        return sensors
    
    def save_to_json(self, sensors: List[Dict[str, Any]], output_file: Optional[Path] = None):
        """Save discovered sensors to JSON file with metadata."""
        if not output_file:
            output_file = PROJECT_ROOT / 'config' / 'sensor_paths_buzios.json'
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Group sensors by platform
        sensors_by_platform = defaultdict(list)
        for sensor in sensors:
            platform = sensor.get('uep', 'UNKNOWN')
            sensors_by_platform[platform].append(sensor)
        
        # Create output structure
        output_data = {
            'metadata': {
                'source': 'PI Builder Excel Export + PI AF Server',
                'excel_file': 'docs/Sensores.xlsx',
                'af_server': self.AF_SERVER,
                'af_database': self.AF_DATABASE,
                'af_path_prefix': self.AF_PATH_PREFIX,
                'discovered_at': datetime.now().isoformat(),
                'total_sensors': len(sensors),
                'platforms': sorted(sensors_by_platform.keys()),
                'mode': 'DEMO' if self.demo_mode else 'REAL',
                'af_connected': self.af_manager is not None,
            },
            'sensors': sensors,
            'sensors_by_platform': {k: v for k, v in sensors_by_platform.items()},
        }
        
        # Save to JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"\n✓ Saved {len(sensors)} sensors to: {output_file}")
        logger.info(f"  Total sensors: {len(sensors)}")
        logger.info(f"  Platforms: {', '.join(sorted(sensors_by_platform.keys()))}")
        
        return output_file
    
    def print_summary(self, sensors: List[Dict[str, Any]]):
        """Print comprehensive discovery summary."""
        if not sensors:
            logger.warning("No sensors to summarize")
            return
        
        logger.info("\n" + "="*80)
        logger.info("DISCOVERY SUMMARY")
        logger.info("="*80)
        
        # By platform
        platforms = defaultdict(int)
        for sensor in sensors:
            platform = sensor.get('uep', 'UNKNOWN')
            platforms[platform] += 1
        
        logger.info(f"\n📍 By Platform ({len(platforms)} total):")
        for platform in sorted(platforms.keys()):
            logger.info(f"   {platform:15} {platforms[platform]:5} sensores")
        
        # By gas type
        gas_types = defaultdict(int)
        for sensor in sensors:
            gas = sensor.get('tipo_gas') or 'N/A'
            gas_types[str(gas)] += 1
        
        logger.info(f"\n⚡ By Gas Type ({len(gas_types)} types):")
        for gas in sorted(gas_types.keys()):
            logger.info(f"   {str(gas):20} {gas_types[gas]:5} sensores")
        
        # By manufacturer
        manufacturers = defaultdict(int)
        for sensor in sensors:
            mfg = sensor.get('fabricante') or 'N/A'
            manufacturers[str(mfg)] += 1
        
        logger.info(f"\n🏭 By Manufacturer ({len(manufacturers)} total):")
        for mfg in sorted(manufacturers.keys()):
            if mfg != 'N/A':
                logger.info(f"   {str(mfg):30} {manufacturers[mfg]:5} sensores")
        if 'N/A' in manufacturers and manufacturers['N/A'] > 0:
            logger.info(f"   {'[Not specified]':30} {manufacturers['N/A']:5} sensores")
        
        # Sample data
        logger.info(f"\n📋 Sample Sensor Data:")
        if sensors:
            sample = sensors[0]
            logger.info(f"   ID: {sample.get('id_af', 'N/A')}")
            logger.info(f"   Descrição: {sample.get('descricao', 'N/A')}")
            logger.info(f"   Tipo Gás: {sample.get('tipo_gas', 'N/A')}")
            logger.info(f"   UEP: {sample.get('uep', 'N/A')}")
            logger.info(f"   Fabricante: {sample.get('fabricante', 'N/A')}")
            logger.info(f"   PATH: {sample.get('path_af', 'N/A')}")
        
        logger.info("\n" + "="*80)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Discover sensors from PI AF using Excel export from PI Builder'
    )
    parser.add_argument('--demo', action='store_true',
                        help='Demo mode: use first 20 sensors, no AF connection')
    parser.add_argument('--max-results', type=int,
                        help='Limit number of sensors to process')
    parser.add_argument('--output', type=Path,
                        help='Output JSON file')
    parser.add_argument('--verbose', action='store_true',
                        help='Enable verbose logging')
    
    args = parser.parse_args()
    
    try:
        # Check dependencies
        if not PANDAS_AVAILABLE:
            logger.error("pandas required. Install with: pip install pandas")
            sys.exit(1)
        
        # Discover sensors
        discovery = SensorDiscoveryFromAF(
            demo_mode=args.demo,
            max_results=args.max_results,
            verbose=args.verbose
        )
        sensors = discovery.discover_sensors()
        
        if not sensors:
            logger.error("No sensors discovered!")
            sys.exit(1)
        
        # Save to JSON
        output_file = discovery.save_to_json(sensors, args.output)
        
        # Print summary
        discovery.print_summary(sensors)
        
        logger.info("\n✅ DISCOVERY COMPLETE")
        logger.info(f"Next step: python scripts/import_sensors_simple.py")
        
    except KeyboardInterrupt:
        logger.info("\n⚠ Discovery cancelled by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
