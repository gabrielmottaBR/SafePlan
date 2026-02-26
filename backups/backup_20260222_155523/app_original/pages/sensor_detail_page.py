"""
Página de Detalhamento Individual de Sensor
Exibe gráficos históricos, dados do sensor, e informações de tratamento/voting groups
"""
import sys
import os
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from config.settings import Config
from src.data.database import DatabaseManager
from src.data.repositories import RepositoryFactory

# Page config
st.set_page_config(
    page_title="Detalhes do Sensor",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Styling
st.markdown("""
    <style>
    .sensor-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 30px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .sensor-title {
        font-size: 32px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .sensor-subtitle {
        font-size: 16px;
        opacity: 0.9;
    }
    .data-card {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin-bottom: 15px;
    }
    .metric-label {
        font-size: 12px;
        color: #666;
        font-weight: bold;
        text-transform: uppercase;
    }
    .metric-value {
        font-size: 20px;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 5px;
    }
    .status-badge {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 12px;
        margin-right: 10px;
    }
    .status-operational {
        background-color: #d4edda;
        color: #155724;
    }
    .status-failure {
        background-color: #fff3cd;
        color: #856404;
    }
    .status-override {
        background-color: #f8d7da;
        color: #721c24;
    }
    </style>
""", unsafe_allow_html=True)

def get_sensor_data(sensor_id_af):
    """Obtém dados do sensor a partir do ID_AF"""
    try:
        db = DatabaseManager(Config.DATABASE_URL)
        repo = RepositoryFactory.create_repository('sensor', db)
        sensor = repo.get_by_id_af(sensor_id_af)
        return sensor
    except Exception as e:
        st.error(f"Erro ao buscar sensor: {e}")
        return None

def get_sensor_readings(sensor_id, hours=24):
    """Obtém leituras do sensor nos últimas N horas"""
    try:
        db = DatabaseManager(Config.DATABASE_URL)
        repo = RepositoryFactory.create_repository('reading', db)
        
        # Buscar leituras do período
        start_date = datetime.now() - timedelta(hours=hours)
        readings = repo.get_readings_for_sensor(sensor_id, start_date, datetime.now())
        
        if readings:
            df = pd.DataFrame([
                {
                    'timestamp': r.timestamp,
                    'value': r.value,
                    'unit': r.unit
                }
                for r in readings
            ])
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            return df.sort_values('timestamp')
        return None
    except Exception as e:
        st.warning(f"Leituras não disponíveis: {e}")
        return None

def get_voting_groups(grupo):
    """Obtém lista de sensores no mesmo grupo de votação"""
    try:
        db = DatabaseManager(Config.DATABASE_URL)
        repo = RepositoryFactory.create_repository('sensor', db)
        sensors = repo.get_by_grupo(grupo)
        return sensors
    except Exception as e:
        st.warning(f"Erro ao buscar grupo: {e}")
        return []

def create_historical_chart(df, title, y_label):
    """Cria gráfico histórico com Plotly"""
    if df is None or df.empty:
        return None
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df['value'],
        mode='lines+markers',
        name='Valor',
        line=dict(color='#667eea', width=2),
        marker=dict(size=4),
        fill='tozeroy',
        fillcolor='rgba(102, 126, 234, 0.2)'
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title='Data/Hora',
        yaxis_title=y_label,
        template='plotly_white',
        hovermode='x unified',
        height=300,
        margin=dict(l=50, r=50, t=50, b=50)
    )
    
    return fig

def main():
    """Função principal"""
    
    # Obter ID_AF dos session state ou query params
    if 'selected_sensor_id' in st.session_state and st.session_state.selected_sensor_id:
        sensor_id_af = st.session_state.selected_sensor_id
    else:
        query_params = st.query_params
        sensor_id_af = query_params.get('sensor_id', None)
    
    if not sensor_id_af:
        st.error("❌ Nenhum sensor selecionado. Por favor, clique em um sensor na tabela de monitoramento.")
        st.info("Você será redirecionado para a página de monitoramento ao voltar.")
        if st.button("← Voltar para Monitoramento", key="back_to_monitoring"):
            if 'selected_sensor_id' in st.session_state:
                del st.session_state.selected_sensor_id
            st.switch_page("pages/monitoring_page.py")
        return
    
    # Buscar dados do sensor
    sensor = get_sensor_data(sensor_id_af)
    
    if not sensor:
        st.error(f"❌ Sensor {sensor_id_af} não encontrado no banco de dados.")
        st.info("Verifique o ID e tente novamente, ou volte à página de monitoramento.")
        if st.button("← Voltar para Monitoramento", key="back_error"):
            if 'selected_sensor_id' in st.session_state:
                del st.session_state.selected_sensor_id
            st.switch_page("pages/monitoring_page.py")
        return
    
    # Header
    st.markdown(f"""
        <div class="sensor-header">
            <div class="sensor-title">🔍 {sensor.id_af}</div>
            <div class="sensor-subtitle">{sensor.descricao or 'Sem descrição'}</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Botão voltar
    col1, col2, col3 = st.columns([1, 8, 1])
    with col1:
        if st.button("← Voltar", key="back_button"):
            # Limpar session state
            if 'selected_sensor_id' in st.session_state:
                del st.session_state.selected_sensor_id
            st.switch_page("pages/monitoring_page.py")
    
    st.markdown("---")
    
    # Informações básicas em 3 colunas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="data-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">🏢 Plataforma</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{sensor.uep or "N/A"}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="data-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">⚗️ Tipo de Gás</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{sensor.tipo_gas or "N/A"}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="data-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">📐 Unidade</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{sensor.tipo_leitura or sensor.unit or "N/A"}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Segunda linha: Grupo e Módulo
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="data-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">🔗 Grupo</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{sensor.grupo or "N/A"}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="data-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">📦 Módulo</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{sensor.modulo or "N/A"}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="data-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">📍 Fabricante</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{sensor.fabricante or "N/A"}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Gráficos históricos
    st.subheader("📈 Histórico de Sensibilização", divider="blue")
    
    # Obter leituras
    readings_df = get_sensor_readings(sensor.sensor_id, hours=24)
    
    if readings_df is not None and not readings_df.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            fig1 = create_historical_chart(readings_df, "Sensibilização (Últimas 24h)", 
                                          f"Valor ({sensor.unit or sensor.tipo_leitura or 'UN'})")
            if fig1:
                st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # Simular diferentes períodos
            readings_7d = get_sensor_readings(sensor.sensor_id, hours=168)
            if readings_7d is not None and not readings_7d.empty:
                fig2 = create_historical_chart(readings_7d, "Sensibilização (Últimos 7 dias)",
                                              f"Valor ({sensor.unit or sensor.tipo_leitura or 'UN'})")
                if fig2:
                    st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("⚠️ Nenhuma leitura disponível para este sensor nos últimos 24 horas.")
    
    st.markdown("---")
    
    # Dados do Sensor e Tratamento
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔧 Dados do Sensor")
        st.markdown(f"""
        **ID do PI AF Server:**
        `{sensor.id_af}`
        
        **Descrição/Tag:**
        {sensor.descricao or "N/A"}
        
        **Grupo:**
        {sensor.grupo or "N/A"}
        
        **Módulo:**
        {sensor.modulo or "N/A"}
        
        **Caminho Completo:**
        `{sensor.path_af or "N/A"}`
        
        **Fabricante:**
        {sensor.fabricante or "N/A"}
        
        **Valores Registrados:**
        - Valor (mA): `{sensor.valor_ma or "N/A"}`
        - Valor (%): `{sensor.valor_pct or "N/A"}`
        """)
    
    with col2:
        st.subheader("⚙️ Configuração de Thresholds")
        st.markdown(f"""
        **Limites de Operação:**
        - OK Inferior: `{sensor.lower_ok_limit or "N/A"}`
        - Aviso Inferior: `{sensor.lower_warning_limit or "N/A"}`
        - Aviso Superior: `{sensor.upper_warning_limit or "N/A"}`
        - Crítico: `{sensor.upper_critical_limit or "N/A"}`
        
        **Status:**
        """ + (f"🟢 **Habilitado**" if sensor.enabled else "🔴 **Desabilitado**"))
    
    st.markdown("---")
    
    # Grupos de Votação
    st.subheader("🔗 Grupo de Votação", divider="blue")
    
    if sensor.grupo:
        st.markdown(f"**Grupo:** `{sensor.grupo}`")
        
        # Buscar outros sensores no mesmo grupo
        voting_group_sensors = get_voting_groups(sensor.grupo)
        
        if voting_group_sensors:
            st.markdown(f"**Sensores no Grupo ({len(voting_group_sensors)}):**")
            
            group_df = pd.DataFrame([
                {
                    'TAG': s.id_af,
                    'Tipo': s.tipo_gas or 'N/A',
                    'Plataforma': s.uep or 'N/A',
                    'Status': '🟢 Habilitado' if s.enabled else '🔴 Desabilitado'
                }
                for s in voting_group_sensors
            ])
            
            st.dataframe(group_df, use_container_width=True, hide_index=True)
            
            # Link para detalhes do grupo
            if st.button("📊 Ver Detalhes do Grupo de Votação", key="view_group"):
                st.session_state.selected_voting_group = sensor.grupo
                st.switch_page("pages/voting_group_detail_page.py")
        else:
            st.info("ℹ️ Nenhum outro sensor encontrado neste grupo.")
    else:
        st.warning("⚠️ Este sensor não está associado a um grupo de votação.")
    
    st.markdown("---")
    
    # Informações de auditoria
    st.caption(f"""
    **Informações de Data:**
    - Criado: {sensor.created_at.strftime('%d/%m/%Y %H:%M:%S') if sensor.created_at else 'N/A'}
    - Atualizado: {sensor.updated_at.strftime('%d/%m/%Y %H:%M:%S') if sensor.updated_at else 'N/A'}
    """)

if __name__ == "__main__":
    main()
