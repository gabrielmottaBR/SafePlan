"""
Unit tests para verificar funcionamento básico da data layer.
"""
import unittest
import os
import tempfile
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

# Add project root to path
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.data.database import DatabaseManager
from src.data.models import SensorConfig, SensorReading, AlertDefinition, AlertHistory
from src.data.repositories import RepositoryFactory


class TestDatabaseManager(unittest.TestCase):
    """Testes para DatabaseManager"""

    def setUp(self):
        """Setup para cada teste - cria BD em memória"""
        self.db_manager = DatabaseManager('sqlite:///:memory:')

    def test_database_connection(self):
        """Testa conexão com banco de dados"""
        self.assertTrue(self.db_manager.health_check())

    def test_create_all_tables(self):
        """Testa criação de todas as tabelas"""
        self.db_manager.create_all_tables()
        self.assertTrue(self.db_manager.health_check())

    def test_get_session(self):
        """Testa obtenção de nova sessão"""
        session = self.db_manager.get_session()
        self.assertIsNotNone(session)
        self.assertIsInstance(session, Session)
        session.close()


class TestSensorConfigRepository(unittest.TestCase):
    """Testes para SensorConfigRepository"""

    def setUp(self):
        """Setup para cada teste"""
        self.db_manager = DatabaseManager('sqlite:///:memory:')
        self.db_manager.create_all_tables()
        self.session = self.db_manager.get_session()
        self.factory = RepositoryFactory(self.session)
        self.sensor_repo = self.factory.sensor_config()

    def tearDown(self):
        """Cleanup após cada teste"""
        self.session.close()

    def test_create_sensor(self):
        """Testa criação de novo sensor"""
        sensor = self.sensor_repo.create(
            internal_name='CH4_P74_01',
            display_name='CH4 Platform 74 - Sensor 01',
            sensor_type='CH4_POINT',
            platform='P74',
            unit='ppm',
            pi_server_tag='P74_CH4_01',
            lower_warning_limit=5.0,
            upper_warning_limit=50.0,
            upper_critical_limit=100.0
        )

        self.assertIsNotNone(sensor)
        self.assertEqual(sensor.internal_name, 'CH4_P74_01')
        self.assertEqual(sensor.platform, 'P74')
        self.assertTrue(sensor.enabled)

    def test_get_sensor_by_id(self):
        """Testa busca de sensor por ID"""
        created = self.sensor_repo.create(
            internal_name='TEST_SENSOR',
            display_name='Test Sensor',
            sensor_type='TEMPERATURE',
            platform='P75',
            unit='°C',
            pi_server_tag='TEST_TAG'
        )

        fetched = self.sensor_repo.get_by_id(created.sensor_id)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.internal_name, 'TEST_SENSOR')

    def test_get_sensor_by_platform(self):
        """Testa busca de sensores por plataforma"""
        self.sensor_repo.create(
            internal_name='P74_SENSOR_1',
            display_name='Sensor 1',
            sensor_type='CH4_POINT',
            platform='P74',
            unit='ppm',
            pi_server_tag='P74_SENSOR_1'
        )

        self.sensor_repo.create(
            internal_name='P74_SENSOR_2',
            display_name='Sensor 2',
            sensor_type='CH4_POINT',
            platform='P74',
            unit='ppm',
            pi_server_tag='P74_SENSOR_2'
        )

        sensors = self.sensor_repo.get_by_platform('P74')
        self.assertEqual(len(sensors), 2)

    def test_update_sensor(self):
        """Testa atualização de sensor"""
        sensor = self.sensor_repo.create(
            internal_name='UPDATE_TEST',
            display_name='Original Name',
            sensor_type='CH4_POINT',
            platform='P76',
            unit='ppm',
            pi_server_tag='UPDATE_TAG'
        )

        updated = self.sensor_repo.update(
            sensor.sensor_id,
            display_name='Updated Name',
            upper_critical_limit=200.0
        )

        self.assertEqual(updated.display_name, 'Updated Name')
        self.assertEqual(updated.upper_critical_limit, 200.0)


class TestSensorReadingRepository(unittest.TestCase):
    """Testes para SensorReadingRepository"""

    def setUp(self):
        """Setup para cada teste"""
        self.db_manager = DatabaseManager('sqlite:///:memory:')
        self.db_manager.create_all_tables()
        self.session = self.db_manager.get_session()
        self.factory = RepositoryFactory(self.session)

        # Create sensor first
        self.sensor_repo = self.factory.sensor_config()
        self.sensor = self.sensor_repo.create(
            internal_name='READING_TEST',
            display_name='Reading Test',
            sensor_type='CH4_POINT',
            platform='P74',
            unit='ppm',
            pi_server_tag='READING_TEST_TAG'
        )

        self.reading_repo = self.factory.sensor_reading()

    def tearDown(self):
        """Cleanup após cada teste"""
        self.session.close()

    def test_create_reading(self):
        """Testa criação de nova leitura"""
        now = datetime.utcnow()
        reading = self.reading_repo.create(
            sensor_id=self.sensor.sensor_id,
            value=25.5,
            timestamp=now,
            unit='ppm',
            data_quality=0
        )

        self.assertIsNotNone(reading)
        self.assertEqual(reading.value, 25.5)
        self.assertEqual(reading.sensor_id, self.sensor.sensor_id)

    def test_get_latest_reading(self):
        """Testa busca da última leitura"""
        now = datetime.utcnow()
        self.reading_repo.create(
            sensor_id=self.sensor.sensor_id,
            value=20.0,
            timestamp=now - timedelta(minutes=10),
            unit='ppm'
        )

        latest = self.reading_repo.create(
            sensor_id=self.sensor.sensor_id,
            value=25.5,
            timestamp=now,
            unit='ppm'
        )

        fetched = self.reading_repo.get_latest(self.sensor.sensor_id)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.value, 25.5)

    def test_get_reading_by_time_range(self):
        """Testa busca de leituras em intervalo de tempo"""
        now = datetime.utcnow()

        for i in range(5):
            self.reading_repo.create(
                sensor_id=self.sensor.sensor_id,
                value=20.0 + i,
                timestamp=now - timedelta(minutes=(5-i)*10),
                unit='ppm'
            )

        start = now - timedelta(minutes=60)
        end = now

        readings = self.reading_repo.get_by_time_range(self.sensor.sensor_id, start, end)
        self.assertEqual(len(readings), 5)


class TestAlertDefinitionRepository(unittest.TestCase):
    """Testes para AlertDefinitionRepository"""

    def setUp(self):
        """Setup para cada teste"""
        self.db_manager = DatabaseManager('sqlite:///:memory:')
        self.db_manager.create_all_tables()
        self.session = self.db_manager.get_session()
        self.factory = RepositoryFactory(self.session)

        # Create sensor first
        self.sensor_repo = self.factory.sensor_config()
        self.sensor = self.sensor_repo.create(
            internal_name='ALERT_TEST',
            display_name='Alert Test',
            sensor_type='CH4_POINT',
            platform='P74',
            unit='ppm',
            pi_server_tag='ALERT_TEST_TAG'
        )

        self.alert_def_repo = self.factory.alert_definition()

    def tearDown(self):
        """Cleanup após cada teste"""
        self.session.close()

    def test_create_alert_definition(self):
        """Testa criação de definição de alerta"""
        alert_def = self.alert_def_repo.create(
            sensor_id=self.sensor.sensor_id,
            condition_type='THRESHOLD',
            severity_level=4,
            threshold_value=100.0
        )

        self.assertIsNotNone(alert_def)
        self.assertEqual(alert_def.condition_type, 'THRESHOLD')
        self.assertEqual(alert_def.severity_level, 4)

    def test_get_alert_by_sensor(self):
        """Testa busca de alertas por sensor"""
        self.alert_def_repo.create(
            sensor_id=self.sensor.sensor_id,
            condition_type='THRESHOLD',
            severity_level=3,
            threshold_value=50.0
        )

        alerts = self.alert_def_repo.get_by_sensor(self.sensor.sensor_id)
        self.assertEqual(len(alerts), 1)


if __name__ == '__main__':
    unittest.main()
