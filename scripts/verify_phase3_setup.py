"""
SafePlan Phase 3 - Setup Verification Script
Verifica se tudo foi instalado corretamente
"""

def check_imports():
    """Verifica se todos os imports funcionam"""
    print("🔍 Verificando imports...")
    
    checks = []
    
    # Core ML imports
    try:
        from src.ml.anomaly_detector import create_anomaly_detector
        checks.append(("✓ Anomaly Detector", True))
    except Exception as e:
        checks.append(("✗ Anomaly Detector", False, str(e)))
    
    try:
        from src.ml.forecaster import create_forecaster
        checks.append(("✓ Time Series Forecaster", True))
    except Exception as e:
        checks.append(("✗ Time Series Forecaster", False, str(e)))
    
    try:
        from src.ml.ml_engine import create_ml_engine
        checks.append(("✓ ML Engine", True))
    except Exception as e:
        checks.append(("✗ ML Engine", False, str(e)))
    
    try:
        from src.ml.repositories import (
            create_prediction_repository,
            create_readings_repository,
            create_training_repository
        )
        checks.append(("✓ ML Repositories", True))
    except Exception as e:
        checks.append(("✗ ML Repositories", False, str(e)))
    
    try:
        from app.pages.predictions_page import render_predictions_page
        checks.append(("✓ Predictions Page", True))
    except Exception as e:
        checks.append(("✗ Predictions Page", False, str(e)))
    
    # Print results
    for check in checks:
        if len(check) == 2:
            print(f"{check[0]}")
        else:
            print(f"{check[0]} - {check[2]}")
    
    return all(c[1] if len(c) > 1 else False for c in checks)


def check_dependencies():
    """Verifica se as dependências estão instaladas"""
    print("\n📦 Verificando dependências...")
    
    requirements = {
        'streamlit': '>=1.28.0',
        'sqlalchemy': '>=2.0',
        'pandas': '>=2.0.0',
        'numpy': '>=1.24.0',
        'scikit-learn': '>=1.3.0',
        'prophet': '>=1.1.4',
        'plotly': '>=5.14.0',
    }
    
    all_ok = True
    
    for package, version in requirements.items():
        try:
            mod = __import__(package)
            print(f"✓ {package} ({version})")
        except ImportError:
            print(f"✗ {package} - NOT INSTALLED")
            all_ok = False
    
    return all_ok


def check_database():
    """Verifica se o banco de dados está inicializado"""
    print("\n🗄️  Verificando banco de dados...")
    
    try:
        from src.data.database import SessionLocal
        from src.data.models import SensorConfig, MLPrediction
        
        session = SessionLocal()
        
        # Check if tables exist
        sensor_count = session.query(SensorConfig).count()
        print(f"✓ Database connected")
        print(f"  - Sensors configured: {sensor_count}")
        
        # Check ML prediction table
        prediction_count = session.query(MLPrediction).count()
        print(f"  - Predictions saved: {prediction_count}")
        
        session.close()
        return True
        
    except Exception as e:
        print(f"✗ Database error: {e}")
        return False


def check_test_data():
    """Verifica se há dados de teste suficientes"""
    print("\n📊 Verificando dados de teste...")
    
    try:
        from src.data.database import SessionLocal
        from src.data.models import SensorConfig, SensorReading
        from datetime import datetime, timedelta
        
        session = SessionLocal()
        
        sensors = session.query(SensorConfig).filter(
            SensorConfig.enabled == True
        ).limit(5).all()
        
        if not sensors:
            print("⚠️  Nenhum sensor encontrado. Adicione sensores via UI.")
            return False
        
        for sensor in sensors:
            reading_count = session.query(SensorReading).filter(
                SensorReading.sensor_id == sensor.sensor_id
            ).count()
            
            status = "✓" if reading_count >= 50 else "⚠️"
            print(f"{status} {sensor.display_name}: {reading_count} readings")
        
        session.close()
        return True
        
    except Exception as e:
        print(f"✗ Error checking data: {e}")
        return False


def test_ml_engine():
    """Testa se o ML Engine funciona"""
    print("\n🧪 Testando ML Engine...")
    
    try:
        from src.ml.ml_engine import create_ml_engine
        import numpy as np
        
        engine = create_ml_engine()
        print("✓ ML Engine criado")
        
        # Test anomaly detection with synthetic data
        test_data = np.random.normal(50, 5, 100)
        engine.anomaly_detectors[999] = __import__('src.ml.anomaly_detector', fromlist=['AnomalyDetector']).AnomalyDetector()
        engine.anomaly_detectors[999].fit(test_data)
        
        predictions, scores = engine.anomaly_detectors[999].detect_ensemble(test_data)
        print(f"✓ Anomaly detection trabajando ({len(predictions)} predictions)")
        
        # Test forecaster
        from datetime import datetime, timedelta
        dates = [datetime.now() - timedelta(hours=i) for i in range(100, 0, -1)]
        values = list(np.random.normal(50, 5, 100))
        
        forecaster = __import__('src.ml.forecaster', fromlist=['TimeSeriesForecaster']).TimeSeriesForecaster()
        forecaster.fit(dates, values)
        print("✓ Time series forecaster trained")
        
        return True
        
    except Exception as e:
        print(f"✗ ML Engine error: {e}")
        return False


def main():
    """Executa todas as verificações"""
    print("="*70)
    print("SafePlan Phase 3 - Setup Verification")
    print("="*70)
    
    results = {
        'imports': check_imports(),
        'dependencies': check_dependencies(),
        'database': check_database(),
        'test_data': check_test_data(),
        'ml_engine': test_ml_engine(),
    }
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    for check, result in results.items():
        status = "✓ OK" if result else "⚠️  WARNING"
        print(f"{status}: {check}")
    
    all_ok = all(results.values())
    
    if all_ok:
        print("\n✅ Tudo OK! SafePlan Phase 3 está pronto para usar.")
        print("\nPróximos passos:")
        print("1. Abrir Dashboard: streamlit run app/main.py")
        print("2. Navegar para 'Predictions' tab")
        print("3. Treinar modelos via 'Training' tab")
        print("4. Ver resultados em 'Forecasting' e 'Anomaly Detection'")
    else:
        print("\n⚠️  Alguns problemas foram encontrados. Verifique acima.")
    
    return all_ok


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
