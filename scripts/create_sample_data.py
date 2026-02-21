"""
SafePlan - Generate Sample Data for Testing
Cria dados de exemplo para testar todas as funcionalidades
"""
import sys
from datetime import datetime, timedelta
import random
import numpy as np

# Add project root to path
sys.path.insert(0, '/'.join(__file__.split('\\')[:-2]))

from src.data.database import DatabaseManager
from src.data.models import SensorConfig, SensorReading, AlertDefinition
from config.settings import Config

# Initialize database
db_manager = DatabaseManager(Config.DATABASE_URL)

def get_session():
    return db_manager.get_session()

def create_sample_sensors():
    """Cria sensores de exemplo"""
    session = get_session()
    
    # Verificar se já existem sensores
    existing_sensors = session.query(SensorConfig).count()
    if existing_sensors > 0:
        print(f"✓ {existing_sensors} sensores já existem no banco de dados")
        session.close()
        return
    
    print("📡 Criando sensores de exemplo...")
    
    sensors_data = [
        # Plataforma P74
        {
            'internal_name': 'P74_CH4_POINT_01',
            'display_name': 'P74 - CH4 Point Detector 01',
            'sensor_type': 'CH4_POINT',
            'platform': 'P74',
            'unit': 'ppm',
            'pi_server_tag': '\\\\SAURIOPIAF02\\DB_BUZIOS_SENSORES\\P74\\CH4_POINT_01',
            'lower_ok_limit': 0.0,
            'lower_warning_limit': 2.0,
            'upper_warning_limit': 5.0,
            'upper_critical_limit': 50.0
        },
        {
            'internal_name': 'P74_H2S_01',
            'display_name': 'P74 - H2S Detector 01',
            'sensor_type': 'H2S',
            'platform': 'P74',
            'unit': 'ppm',
            'pi_server_tag': '\\\\SAURIOPIAF02\\DB_BUZIOS_SENSORES\\P74\\H2S_01',
            'lower_ok_limit': 0.0,
            'lower_warning_limit': 0.5,
            'upper_warning_limit': 1.0,
            'upper_critical_limit': 10.0
        },
        {
            'internal_name': 'P74_TEMPERATURE_01',
            'display_name': 'P74 - Temperature Sensor 01',
            'sensor_type': 'TEMPERATURE',
            'platform': 'P74',
            'unit': '°C',
            'pi_server_tag': '\\\\SAURIOPIAF02\\DB_BUZIOS_SENSORES\\P74\\TEMP_01',
            'lower_ok_limit': -10.0,
            'lower_warning_limit': 20.0,
            'upper_warning_limit': 60.0,
            'upper_critical_limit': 80.0
        },
        # Plataforma P75
        {
            'internal_name': 'P75_CH4_POINT_01',
            'display_name': 'P75 - CH4 Point Detector 01',
            'sensor_type': 'CH4_POINT',
            'platform': 'P75',
            'unit': 'ppm',
            'pi_server_tag': '\\\\SAURIOPIAF02\\DB_BUZIOS_SENSORES\\P75\\CH4_POINT_01',
            'lower_ok_limit': 0.0,
            'lower_warning_limit': 2.0,
            'upper_warning_limit': 5.0,
            'upper_critical_limit': 50.0
        },
        {
            'internal_name': 'P75_FLAME_01',
            'display_name': 'P75 - Flame Detector 01',
            'sensor_type': 'FLAME',
            'platform': 'P75',
            'unit': 'status',
            'pi_server_tag': '\\\\SAURIOPIAF02\\DB_BUZIOS_SENSORES\\P75\\FLAME_01',
            'lower_ok_limit': 0.0,
            'lower_warning_limit': 1.0,
            'upper_warning_limit': 2.0,
            'upper_critical_limit': 3.0
        },
        # Plataforma FPAB
        {
            'internal_name': 'FPAB_CO2_01',
            'display_name': 'FPAB - CO2 Detector 01',
            'sensor_type': 'CO2',
            'platform': 'FPAB',
            'unit': 'ppm',
            'pi_server_tag': '\\\\SAURIOPIAF02\\DB_BUZIOS_SENSORES\\FPAB\\CO2_01',
            'lower_ok_limit': 0.0,
            'lower_warning_limit': 100.0,
            'upper_warning_limit': 5000.0,
            'upper_critical_limit': 10000.0
        },
        {
            'internal_name': 'FPAB_SMOKE_01',
            'display_name': 'FPAB - Smoke Detector 01',
            'sensor_type': 'SMOKE',
            'platform': 'FPAB',
            'unit': 'status',
            'pi_server_tag': '\\\\SAURIOPIAF02\\DB_BUZIOS_SENSORES\\FPAB\\SMOKE_01',
            'lower_ok_limit': 0.0,
            'lower_warning_limit': 1.0,
            'upper_warning_limit': 2.0,
            'upper_critical_limit': 3.0
        },
    ]
    
    for sensor_data in sensors_data:
        sensor = SensorConfig(**sensor_data)
        session.add(sensor)
    
    session.commit()
    print(f"✓ {len(sensors_data)} sensores criados com sucesso")
    session.close()


def create_sample_readings():
    """Cria leituras de exemplo para os últimos 7 dias"""
    session = get_session()
    
    sensors = session.query(SensorConfig).all()
    
    if not sensors:
        print("❌ Nenhum sensor encontrado")
        session.close()
        return
    
    print("📊 Gerando leituras de exemplo (últimos 7 dias)...")
    
    readings_created = 0
    now = datetime.utcnow()
    
    for sensor in sensors:
        # Gerar 168 pontos (7 dias x 24 horas)
        for hours_ago in range(168, 0, -1):
            timestamp = now - timedelta(hours=hours_ago)
            
            # Gerar valor com padrão + ruído
            if sensor.sensor_type in ['FLAME', 'SMOKE']:
                # Valores binários para detectores
                value = random.choice([0.0, 0.5, 1.0]) if random.random() > 0.95 else 0.0
            elif sensor.sensor_type == 'TEMPERATURE':
                # Temperatura segue padrão de 25°C ± 5°C
                value = 25 + random.gauss(0, 2)
            elif sensor.sensor_type == 'CH4_POINT':
                # CH4 em 2 ppm ± 0.5 ppm, com outliers ocasionais
                value = 2.0 + random.gauss(0, 0.3)
                if random.random() > 0.95:  # 5% chance de anomalia
                    value = random.uniform(20, 40)
            else:
                # Valores padrão
                value = 50 + random.gauss(0, 5)
            
            reading = SensorReading(
                sensor_id=sensor.sensor_id,
                value=max(0, value),  # Sem valores negativos
                timestamp=timestamp,
                unit=sensor.unit,
                data_quality=0  # Good quality
            )
            session.add(reading)
            readings_created += 1
    
    session.commit()
    print(f"✓ {readings_created} leituras criadas com sucesso")
    session.close()


def create_sample_alert_definitions():
    """Cria definições de alertas para os sensores"""
    session = get_session()
    
    sensors = session.query(SensorConfig).all()
    
    print("⚠️ Criando definições de alertas...")
    
    alerts_created = 0
    
    for sensor in sensors:
        # Alert de aviso (warning)
        alert_warning = AlertDefinition(
            sensor_id=sensor.sensor_id,
            condition_type='THRESHOLD',
            severity_level=2,  # Warning
            threshold_value=sensor.upper_warning_limit if sensor.upper_warning_limit else 50,
            enabled=True
        )
        session.add(alert_warning)
        alerts_created += 1
        
        # Alert crítico (critical)
        alert_critical = AlertDefinition(
            sensor_id=sensor.sensor_id,
            condition_type='THRESHOLD',
            severity_level=4,  # Critical
            threshold_value=sensor.upper_critical_limit if sensor.upper_critical_limit else 100,
            enabled=True
        )
        session.add(alert_critical)
        alerts_created += 1
    
    session.commit()
    print(f"✓ {alerts_created} definições de alertas criadas")
    session.close()


def main():
    print("="*70)
    print("SafePlan - Generate Sample Data")
    print("="*70)
    
    try:
        create_sample_sensors()
        create_sample_readings()
        create_sample_alert_definitions()
        
        print("\n" + "="*70)
        print("✅ Dados de exemplo criados com sucesso!")
        print("="*70)
        print("\nVocê pode agora:")
        print("1. Abrir o dashboard: streamlit run app/main.py")
        print("2. Testar todas as funcionalidades:")
        print("   - Dashboard: Visualizar sensores em tempo real")
        print("   - Alerts: Gerenciar alertas")
        print("   - Configuration: Gerenciar sensores")
        print("   - Predictions: ML features (treinar modelos, fazer forecasts)")
        print("   - Reports: Gerar relatórios (quando implementado)")
        print("   - DevTools: Debugging e info")
        
    except Exception as e:
        print(f"❌ Erro ao criar dados de exemplo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
