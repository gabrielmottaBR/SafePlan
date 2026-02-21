"""
Script para gerar leituras realistas de sensores para teste do monitoramento.
Cria dados de teste baseados em padrões realistas dos sensores.
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
        
        for sensor in all_sensors:
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
                
                if added_count % 500 == 0:
                    print(f"  ✓ {added_count} leituras criadas...")
        
        session.commit()
        print(f"\n✅ {added_count} leituras de sensores geradas com sucesso!")
        print(f"\n{'='*80}\n")
        
    except Exception as e:
        print(f"Erro ao gerar leituras: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    print("\nGerando dados para página de Monitoramento...")
    print("Isso criará ~100K de leituras realistas para análise.")
    
    response = input("Continuar? (s/n): ").strip().lower()
    if response == 's':
        generate_readings()
        print("Dados gerados! Acesse: streamlit run app/main.py")
        print("E navegue para a página 'Monitoramento de Sensores'")
    else:
        print("Cancelado.")
