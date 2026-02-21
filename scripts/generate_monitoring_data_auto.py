"""
Script para gerar leituras realistas de sensores - versão automática (sem prompt).
"""
import os
import sys
import json
import random
from datetime import datetime, timedelta

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from config.settings import Config
from src.data.database import DatabaseManager
from src.data.repositories import RepositoryFactory

def generate_readings():
    """Gera leituras realistas para sensores"""
    
    db_manager = DatabaseManager(Config.DATABASE_URL)
    session = db_manager.get_session()
    
    try:
        repos = RepositoryFactory(session)
        sensor_repo = repos.sensor_config()
        reading_repo = repos.sensor_reading()
        
        all_sensors = sensor_repo.get_all()
        
        print(f"\n{'='*80}")
        print("Gerando Leituras para Monitoramento")
        print(f"{'='*80}\n")
        print(f"Total de sensores encontrados: {len(all_sensors)}")
        
        # Padrões de leitura por tipo
        sensor_ranges = {
            'CH4_POINT': {
                'normal': (0, 10),
                'warning': (10, 50),
                'critical': (50, 100),
                'unit': '%LEL'
            },
            'CH4_PLUME': {
                'normal': (0, 5),
                'warning': (5, 25),
                'critical': (25, 100),
                'unit': '%LEL'
            },
            'H2S': {
                'normal': (0, 1),
                'warning': (1, 10),
                'critical': (10, 20),
                'unit': 'ppm'
            },
            'CO2': {
                'normal': (0, 500),
                'warning': (500, 1000),
                'critical': (1000, 5000),
                'unit': 'ppm'
            },
            'H2': {
                'normal': (0, 4),
                'warning': (4, 20),
                'critical': (20, 100),
                'unit': '%LEL'
            },
            'O2': {
                'normal': (18, 21),
                'warning': (16, 18),
                'critical': (0, 16),
                'unit': '%'
            }
        }
        
        added_count = 0
        now = datetime.now()
        
        for idx, sensor in enumerate(all_sensors):
            if idx % 100 == 0 and idx > 0:
                print(f"  📊 Processando sensor {idx}/{len(all_sensors)}...")
            
            # Obtém padrão para o tipo de sensor
            sensor_type = sensor.sensor_type
            pattern = sensor_ranges.get(sensor_type, sensor_ranges['CH4_POINT'])
            
            # Gera 30 leituras nos últimos 30 minutos
            for i in range(30):
                # 70% normal, 20% warning, 10% critical
                rand = random.random()
                if rand < 0.7:
                    value = random.uniform(pattern['normal'][0], pattern['normal'][1])
                elif rand < 0.9:
                    value = random.uniform(pattern['warning'][0], pattern['warning'][1])
                else:
                    value = random.uniform(pattern['critical'][0], pattern['critical'][1])
                
                # Adiciona ruído
                value += random.gauss(0, pattern['normal'][1] * 0.1)
                value = max(0, value)  # Evita valores negativos
                
                # Cria leitura
                timestamp = now - timedelta(minutes=30-i)
                reading = reading_repo.create(
                    sensor_id=sensor.sensor_id,
                    value=round(value, 2),
                    timestamp=timestamp,
                    unit=pattern.get('unit'),
                    data_quality=100
                )
                added_count += 1
                
                if added_count % 5000 == 0:
                    print(f"  ✓ {added_count} leituras criadas...")
        
        print(f"\n✅ Total de {added_count} leituras de sensores geradas!")
        print(f"   Sensores com dados: {len(all_sensors)}")
        print(f"   Média de leituras por sensor: {added_count // len(all_sensors) if all_sensors else 0}")
        print(f"\n{'='*80}\n")
        
    except Exception as e:
        print(f"❌ Erro ao gerar leituras: {e}")
        import traceback
        traceback.print_exc()
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    generate_readings()
