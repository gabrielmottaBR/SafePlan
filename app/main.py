"""
SafePlan - Main Streamlit Application
Aplicação principal que configura páginas e layout do dashboard.
"""
import streamlit as st
import logging
from datetime import datetime

from config.settings import Config
from src.data.database import init_database
from src.alerting.alert_engine import create_alert_engine
from src.sensors.sensor_manager import create_sensor_manager

# Configure page
st.set_page_config(
    page_title="SafePlan - Fire & Gas Monitoring",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configure logging
logging.basicConfig(
    level=Config.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@st.cache_resource
def initialize_app():
    """Inicializa aplicação (cache para evitar reinicializações)"""
    # Initialize database
    db = init_database(Config.DATABASE_URL)
    logger.info("✓ Database inicializado")

    # Create managers
    alert_engine = create_alert_engine()
    sensor_manager = create_sensor_manager()

    return {
        'db': db,
        'alert_engine': alert_engine,
        'sensor_manager': sensor_manager
    }


def render_header():
    """Renderiza header da aplicação"""
    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        st.title("🔥 SafePlan")
        st.markdown("**Fire & Gas Monitoring System**")

    with col2:
        st.markdown("### Petrobras Offshore Platforms")
        st.markdown("*Advanced Real-time Monitoring Dashboard*")

    with col3:
        st.markdown(f"**Time:** {datetime.now().strftime('%H:%M:%S')}")
        st.markdown(f"**Date:** {datetime.now().strftime('%d/%m/%Y')}")


def render_sidebar():
    """Renderiza sidebar com navegação"""
    with st.sidebar:
        st.image("https://via.placeholder.com/150?text=Petrobras", width=150)

        st.markdown("---")
        st.markdown("### 📊 Navigation")

        app_state = {
            'page': st.radio(
                "Select Page",
                ["Dashboard", "Alerts", "Predictions", "Configuration", "Reports", "DevTools"],
                index=0
            )
        }

        st.markdown("---")
        st.markdown("### ℹ️ Quick Stats")

        try:
            app = initialize_app()
            stats = app['alert_engine'].get_alert_statistics()

            col1, col2 = st.columns(2)
            with col1:
                st.metric("🔴 Critical", stats.get('critical', 0))
                st.metric("⚠️ Warnings", stats.get('warning', 0))

            with col2:
                st.metric("🚨 Danger", stats.get('danger', 0))
                st.metric("Total Active", stats.get('total_active', 0))

        except Exception as e:
            logger.error(f"Erro ao carregar estatísticas: {e}")
            st.error("Erro ao carregar estatísticas")

        st.markdown("---")
        st.markdown("### 🔧 Settings")

        if st.checkbox("Debug Mode"):
            st.session_state.debug_mode = True
        else:
            st.session_state.debug_mode = False

        st.markdown("---")
        st.markdown("### 📚 About")
        st.markdown("""
        **SafePlan v0.1.0**

        Professional monitoring platform for Petrobras offshore
        fire and gas detection systems.

        - **Sensors:** 9+ types monitored
        - **Platforms:** 9 platforms (P74-P79, FPAB, FPAT)
        - **ML:** Anomaly detection + Forecasting
        - **Alerts:** 4 severity levels
        - **Integration:** Microsoft Teams
        """)

        return app_state


def main():
    """Main application entry point"""
    try:
        # Initialize components
        app = initialize_app()

        # Render layout
        render_header()
        app_state = render_sidebar()

        # Router to pages
        page = app_state.get('page', 'Dashboard')

        if page == "Dashboard":
            st.markdown("---")
            render_dashboard_page(app)

        elif page == "Alerts":
            st.markdown("---")
            render_alerts_page(app)

        elif page == "Predictions":
            st.markdown("---")
            st.info("🚧 Predictions page coming in Phase 3 (ML Integration)")

        elif page == "Configuration":
            st.markdown("---")
            render_configuration_page(app)

        elif page == "Reports":
            st.markdown("---")
            st.info("🚧 Reports page coming in Phase 4 (Advanced UI & Reporting)")

        elif page == "DevTools":
            st.markdown("---")
            render_devtools_page(app)

    except Exception as e:
        logger.error(f"Erro na aplicação: {e}")
        st.error(f"❌ Erro na aplicação: {e}")


def render_dashboard_page(app):
    """Renderiza página de Dashboard"""
    st.header("📊 Dashboard - Real-time Monitoring")

    try:
        sensor_manager = app['sensor_manager']
        sensors = sensor_manager.get_enabled_sensors()

        if not sensors:
            st.warning("⚠️ Nenhum sensor configurado. Vá para Configuration para adicionar sensores.")
            return

        # Display sensor metrics
        st.subheader("🌍 Plataformas")

        platforms = sensor_manager.get_platforms()
        cols = st.columns(len(platforms) if platforms else 1)

        for idx, platform in enumerate(platforms):
            with cols[idx]:
                platform_sensors = sensor_manager.get_platform_sensors(platform)
                st.metric(platform, f"{len(platform_sensors)} sensores")

        st.divider()

        # Display sensors
        st.subheader("📡 Sensores")

        for sensor in sensors[:10]:  # Show first 10 sensors
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    sensor.display_name,
                    f"Tipo: {sensor.sensor_type}"
                )

            with col2:
                st.markdown(f"**Plataforma:** {sensor.platform}")
                st.markdown(f"**Unidade:** {sensor.unit}")

            with col3:
                st.markdown(f"**Thresholds:**")
                st.markdown(f"- Warning: {sensor.upper_warning_limit}")
                st.markdown(f"- Critical: {sensor.upper_critical_limit}")

            with col4:
                if st.button(f"View Details", key=f"sensor_{sensor.sensor_id}"):
                    st.session_state.selected_sensor = sensor.sensor_id

        st.divider()
        st.info("💡 Auto-refresh habilitado (20-30s). Página será atualizada automaticamente.")

    except Exception as e:
        logger.error(f"Erro ao renderizar Dashboard: {e}")
        st.error(f"Erro ao carregar Dashboard: {e}")


def render_alerts_page(app):
    """Renderiza página de Alertas"""
    st.header("🚨 Alerts - Alert Management")

    try:
        alert_engine = app['alert_engine']

        st.subheader("🔴 Active Alerts")

        active_alerts = alert_engine.get_active_alerts()

        if not active_alerts:
            st.success("✓ No active alerts")
        else:
            for alert in active_alerts[:20]:  # Show first 20
                col1, col2, col3 = st.columns([2, 1, 1])

                severity_emoji = {
                    1: "✓",
                    2: "⚠️",
                    3: "🔴",
                    4: "🚨"
                }

                with col1:
                    st.markdown(
                        f"**{severity_emoji.get(alert.severity_level)} Alert #{alert.alert_id}**"
                    )
                    st.markdown(f"Sensor: {alert.sensor_id}")
                    st.markdown(f"Value: {alert.sensor_value:.2f}")
                    st.markdown(f"Notes: {alert.notes or 'N/A'}")

                with col2:
                    st.markdown(f"**Status:** {alert.status}")
                    st.markdown(f"**Triggered:** {alert.triggered_at.strftime('%H:%M:%S')}")

                with col3:
                    if alert.status == "ACTIVE":
                        if st.button("Acknowledge", key=f"ack_{alert.alert_id}"):
                            alert_engine.acknowledge_alert(alert.alert_id)
                            st.rerun()

                        if st.button("Resolve", key=f"res_{alert.alert_id}"):
                            alert_engine.resolve_alert(alert.alert_id)
                            st.rerun()

                st.divider()

    except Exception as e:
        logger.error(f"Erro ao renderizar Alerts: {e}")
        st.error(f"Erro ao carregar Alertas: {e}")


def render_configuration_page(app):
    """Renderiza página de Configuração"""
    st.header("⚙️ Configuration - Sensor Management")

    try:
        sensor_manager = app['sensor_manager']

        tab1, tab2, tab3 = st.tabs(["List Sensors", "Add Sensor", "Alert Rules"])

        with tab1:
            st.subheader("Existing Sensors")

            sensors = sensor_manager.get_all_sensors()

            if sensors:
                for sensor in sensors:
                    with st.expander(f"🔹 {sensor.display_name} ({sensor.platform})"):
                        col1, col2 = st.columns(2)

                        with col1:
                            st.markdown(f"**Internal Name:** {sensor.internal_name}")
                            st.markdown(f"**Type:** {sensor.sensor_type}")
                            st.markdown(f"**Platform:** {sensor.platform}")
                            st.markdown(f"**Unit:** {sensor.unit}")

                        with col2:
                            st.markdown(f"**PI Server Tag:** {sensor.pi_server_tag}")
                            st.markdown(f"**Enabled:** {sensor.enabled}")
                            st.markdown(f"**Created:** {sensor.created_at.strftime('%d/%m/%Y')}")

                        st.divider()
                        st.markdown("**Thresholds:**")
                        st.write({
                            'lower_ok': sensor.lower_ok_limit,
                            'lower_warning': sensor.lower_warning_limit,
                            'upper_warning': sensor.upper_warning_limit,
                            'upper_critical': sensor.upper_critical_limit
                        })

            else:
                st.info("No sensors configured yet")

        with tab2:
            st.subheader("Add New Sensor")

            with st.form("add_sensor_form"):
                internal_name = st.text_input("Internal Name (unique)")
                display_name = st.text_input("Display Name")
                sensor_type = st.selectbox(
                    "Sensor Type",
                    ["CH4_POINT", "CH4_PLUME", "CO2", "H2S", "SMOKE", "TEMPERATURE", "FLAME", "H2", "O2"]
                )
                platform = st.selectbox(
                    "Platform",
                    ["P74", "P75", "P76", "P77", "P78", "P79", "FPAB", "FPAT"]
                )
                unit = st.text_input("Unit (e.g., ppm, °C)")
                pi_server_tag = st.text_input("PI Server Tag")

                col1, col2 = st.columns(2)
                with col1:
                    upper_warning = st.number_input("Upper Warning Limit", value=50.0)
                    upper_critical = st.number_input("Upper Critical Limit", value=100.0)

                with col2:
                    lower_warning = st.number_input("Lower Warning Limit", value=0.0)
                    lower_ok = st.number_input("Lower OK Limit", value=-10.0)

                if st.form_submit_button("Add Sensor"):
                    sensor = sensor_manager.create_sensor(
                        internal_name=internal_name,
                        display_name=display_name,
                        sensor_type=sensor_type,
                        platform=platform,
                        unit=unit,
                        pi_server_tag=pi_server_tag,
                        lower_ok_limit=lower_ok,
                        lower_warning_limit=lower_warning,
                        upper_warning_limit=upper_warning,
                        upper_critical_limit=upper_critical
                    )

                    if sensor:
                        st.success(f"✓ Sensor {internal_name} added successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Error adding sensor")

        with tab3:
            st.subheader("Alert Rules")
            st.info("Alert rules management coming soon")

    except Exception as e:
        logger.error(f"Erro ao renderizar Configuration: {e}")
        st.error(f"Erro ao carregar Configuration: {e}")


def render_devtools_page(app):
    """Renderiza página de Dev Tools"""
    st.header("🔧 Dev Tools - Debugging")

    try:
        st.subheader("Database Status")

        db = app['db']

        if db.health_check():
            st.success(f"✓ Database connected: {Config.DATABASE_URL}")
        else:
            st.error(f"❌ Database connection failed")

        st.subheader("Configuration")
        st.json(Config.get_summary())

        if st.checkbox("Show debug info"):
            st.subheader("Debug Info")
            st.write(f"Log Level: {Config.LOG_LEVEL}")
            st.write(f"Debug Mode: {Config.DEBUG_MODE}")
            st.write(f"Current Time: {datetime.now()}")

    except Exception as e:
        logger.error(f"Erro ao renderizar DevTools: {e}")
        st.error(f"Erro ao carregar DevTools: {e}")


if __name__ == "__main__":
    main()
