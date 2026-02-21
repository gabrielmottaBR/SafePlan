"""
Script otimizado para gerar leituras realistas de sensores com bulk inserts.
Muito mais rápido que versão anterior.
"""
import os
import sys
import random
from datetime import datetime, timedelta
from sqlalchemy import insert

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from config.settings import Config
from src.data.database import DatabaseManager
from src.data.models import SensorReading
from src.data.repositories import RepositoryFactory

def generate_readings_optimized(readings_per_sensor=10):
    """Gera leituras usando bulk insert (muito mais rápido)"""
    
    db_manager = DatabaseManager(Config.DATABASE_URL)
    session = db_manager.get_session()
    
    try:
        repos = RepositoryFactory(session)
        sensor_repo = repos.sensor_config()
        
        all_sensors = sensor_repo.get_all()
        
        print(f"\n{'='*80}")
        print("Gerando Leituras para Monitoramento (Otimizado)")
        print(f"{'='*80}\n")
        print(f"Total de sensores: {len(all_sensors)}")
        print(f"Leituras por sensor: {readings_per_sensor}")
        print(f"Total estimado: {len(all_sensors) * readings_per_sensor} leituras\n")
        
        # Padrões de leitura por tipo
        sensor_ranges = {
            'CH4_POINT': ('%LEL', 0, 100),
            'CH4_PLUME': ('%LEL', 0, 100),
            'H2S': ('ppm', 0, 20),
            'CO2': ('ppm', 0, 5000),
            'H2': ('%LEL', 0, 100),
            'O2': ('%', 0, 25)
        }
        
        # Prepara bulk insert
        readings_to_insert = []
        now = datetime.now()
        
        for idx, sensor in enumerate(all_sensors):
            if idx % 500 == 0 and idx > 0:
                print(f"  📊 Preparando sensor {idx}/{len(all_sensors)}...")
            
            sensor_type = sensor.sensor_type
            unit, min_val, max_val = sensor_ranges.get(sensor_type, ('%LEL', 0, 100))
            
            # Gera N leituras nos últimos N minutos
            for i in range(readings_per_sensor):
                # Valor aleatório
                value = random.uniform(min_val, max_val)
                timestamp = now - timedelta(minutes=readings_per_sensor-i)
                
                readings_to_insert.append({
                    'sensor_id': sensor.sensor_id,
                    'value': round(value, 2),
                    'timestamp': timestamp,
                    'unit': unit,
                    'data_quality': 100
                })
        
        # Insere em batches
        print(f"\n  ⚡ Inserindo {len(readings_to_insert)} leituras em batches...")
        batch_size = 5000
        for i in range(0, len(readings_to_insert), batch_size):
            batch = readings_to_insert[i:i+batch_size]
            stmt = insert(SensorReading).values(batch)
            session.execute(stmt)
            session.commit()
            print(f"    ✓ {min(i+batch_size, len(readings_to_insert))}/{len(readings_to_insert)} leituras inseridas")
        
        print(f"\n✅ Total de {len(readings_to_insert)} leituras de sensores geradas!")
        print(f"{'='*80}\n")
        
    except Exception as e:
        print(f"❌ Erro ao gerar leituras: {e}")
        import traceback
        traceback.print_exc()
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    # Gera 10 leituras por sensor (~35k leituras total para 3522 sensores)
    # Se quiser mais dados, aumente o parâmetro
    generate_readings_optimized(readings_per_sensor=10)
