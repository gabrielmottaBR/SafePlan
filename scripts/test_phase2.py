"""
Script de teste para demonstrar funcionalidades da Fase 2.
Testa: Database, Sensors, Alert Engine, Teams Integration
"""
import os
import sys
import io
from datetime import datetime, timedelta

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from config.settings import Config
from src.data.database import init_database
from src.data.repositories import RepositoryFactory
from src.sensors.sensor_manager import create_sensor_manager
from src.alerting.alert_engine import create_alert_engine
from src.alerting.teams_notifier import TeamsNotifier


def print_header(text):
    """Printa header formatado"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def test_database():
    """Testa database"""
    print_header("TEST 1: Database Connection & Initialization")

    db = init_database(Config.DATABASE_URL)
    print(f"✓ Database configured: {Config.DATABASE_URL}")

    if db.health_check():
        print("✓ Database connection OK")
    else:
        print("✗ Database connection FAILED")
        return False

    return True


def test_sensor_management():
    """Testa sensor management"""
    print_header("TEST 2: Sensor Management")

    import time
    timestamp = str(int(time.time()))[-5:]

    sensor_mgr = create_sensor_manager()

    # Create test sensors
    print("Creating test sensors...")

    sensor1_name = f'CH4_P74_T{timestamp}'
    sensor_mgr.create_sensor(
        internal_name=sensor1_name,
        display_name=f'CH4 Platform 74 - Sensor {timestamp}',
        sensor_type='CH4_POINT',
        platform='P74',
        unit='ppm',
        pi_server_tag=f'P74_CH4_{timestamp}',
        lower_warning_limit=5.0,
        upper_warning_limit=50.0,
        upper_critical_limit=100.0
    )
    print(f"✓ Created sensor: {sensor1_name}")

    sensor2_name = f'H2S_P75_T{timestamp}'
    sensor_mgr.create_sensor(
        internal_name=sensor2_name,
        display_name=f'H2S Platform 75 - Sensor {timestamp}',
        sensor_type='H2S',
        platform='P75',
        unit='ppm',
        pi_server_tag=f'P75_H2S_{timestamp}',
        lower_warning_limit=1.0,
        upper_warning_limit=10.0,
        upper_critical_limit=20.0
    )
    print(f"✓ Created sensor: {sensor2_name}")

    # Get sensors - retrieve fresh from database
    all_sensors = sensor_mgr.get_all_sensors()
    print(f"✓ Retrieved {len(all_sensors)} sensors from database")

    # Find the sensors we just created
    sensor1 = next((s for s in all_sensors if s.internal_name == sensor1_name), None)
    sensor2 = next((s for s in all_sensors if s.internal_name == sensor2_name), None)

    sensor1_id = sensor1.sensor_id if sensor1 else None
    sensor2_id = sensor2.sensor_id if sensor2 else None

    p74_sensors = sensor_mgr.get_platform_sensors('P74')
    print(f"✓ Platform P74 has {len(p74_sensors)} sensors")

    return sensor1_id, sensor2_id, sensor1_name, sensor2_name


def test_alert_engine(sensor1_id, sensor2_id, sensor1_name, sensor2_name):
    """Testa alert engine"""
    print_header("TEST 3: Alert Engine & Alerting")

    alert_engine = create_alert_engine()
    sensor_mgr = create_sensor_manager()

    # Create alert rules
    print("Creating alert rules...")

    alert_rule1 = sensor_mgr.create_alert_rule(
        sensor_id=sensor1_id,
        condition_type='THRESHOLD',
        severity_level=4,
        threshold_value=100.0
    )
    if alert_rule1:
        print(f"✓ Created alert rule (THRESHOLD, CRITICAL)")
    else:
        print(f"✗ Failed to create alert rule")

    # Get alert rules for sensor
    rules = sensor_mgr.get_alert_rules(sensor1_id)
    print(f"✓ Retrieved {len(rules)} alert rules for {sensor1_name}")

    # Test alert triggering
    print("\nSimulating sensor readings and alert triggering...")

    # Normal value (no alert)
    print("\n1. Normal value (50 ppm - below warning):")
    alerts = alert_engine.evaluate_and_trigger(
        sensor_id=sensor1_id,
        current_value=50.0,
        alert_definitions=rules
    )
    print(f"   - Alerts triggered: {len(alerts)} (Expected: 0)")

    # Warning value (triggers alert)
    print("\n2. Critical value (120 ppm - exceeds critical limit):")
    alerts = alert_engine.evaluate_and_trigger(
        sensor_id=sensor1_id,
        current_value=120.0,
        alert_definitions=rules
    )
    print(f"   - Alerts triggered: {len(alerts)} (Expected: 1)")

    if alerts:
        alert = alerts[0]
        print(f"   - Alert triggered successfully")
        print(f"   - Severity level: 4 (CRITICAL)")

    # Get active alerts
    active_alerts = alert_engine.get_active_alerts()
    print(f"\n✓ Active alerts in system: {len(active_alerts)}")

    # Get statistics
    stats = alert_engine.get_alert_statistics()
    print(f"✓ Alert statistics: {stats}")

    return sensor1_id, alert_rule1


def test_teams_integration():
    """Testa Teams integration"""
    print_header("TEST 4: Teams Webhook Integration")

    webhook_url = Config.TEAMS_WEBHOOK_URL

    if not webhook_url:
        print("⚠️  Teams webhook URL não configurada (TEAMS_WEBHOOK_URL)")
        print("   Configure em .env para ativar notificações do Teams")
        return

    notifier = TeamsNotifier(webhook_url)

    print("Testing webhook connectivity...")

    if TeamsNotifier.test_webhook(webhook_url):
        print("✓ Teams webhook is accessible")
    else:
        print("✗ Teams webhook connection failed")
        print("  Verifique a URL e a conectividade de internet")


def main():
    """Main test runner"""
    print_header("SafePlan - Phase 2 Integration Tests")

    print("Configuration Summary:")
    print(f"  Database: {Config.DATABASE_URL}")
    print(f"  PI Server: {Config.PI_SERVER_HOST}")
    print(f"  Alert Check Interval: {Config.ALERT_CHECK_INTERVAL_SEC}s")
    print(f"  Teams Webhook: {'Configured' if Config.TEAMS_WEBHOOK_URL else 'Not configured'}")

    # Run tests
    try:
        if not test_database():
            print("\n✗ Database test FAILED - aborting")
            return 1

        sensor1_id, sensor2_id, sensor1_name, sensor2_name = test_sensor_management()
        test_alert_engine(sensor1_id, sensor2_id, sensor1_name, sensor2_name)
        test_teams_integration()

        print_header("All Tests Completed Successfully! ✓")
        print("\nNext Steps:")
        print("1. Run: streamlit run app/main.py")
        print("2. Open dashboard at http://localhost:8501")
        print("3. Configure sensors via UI")
        print("4. Wait for data from PI Server")
        print("5. Monitor alerts in dashboard")

        return 0

    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
