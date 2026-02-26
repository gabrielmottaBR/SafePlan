"""
Página de Detalhamento do Grupo de Votação
Exibe histórico agregado, sensores membros, e estatísticas do grupo
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
    page_title="Detalhes do Grupo de Votação",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Styling
st.markdown("""
    <style>
    .group-header {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 30px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .group-title {
        font-size: 32px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .group-subtitle {
        font-size: 16px;
        opacity: 0.9;
    }
    .sensor-card {
        background: white;
        border: 2px solid #f0f0f0;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 10px;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .sensor-card:hover {
        border-color: #f5576c;
        box-shadow: 0 4px 12px rgba(245, 87, 108, 0.2);
    }
    .sensor-name {
        font-weight: bold;
        font-size: 16px;
        color: #2c3e50;
        margin-bottom: 8px;
    }
    .sensor-meta {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr;
        gap: 10px;
        font-size: 12px;
        color: #666;
    }
    .stat-box {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
    }
    .stat-number {
        font-size: 28px;
        font-weight: bold;
        color: #f5576c;
        margin-bottom: 5px;
    }
    .stat-label {
        font-size: 12px;
        color: #666;
        text-transform: uppercase;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

def get_voting_group_sensors(grupo):
    """Obtém todos os sensores de um grupo de votação"""
    try:
        db = DatabaseManager(Config.DATABASE_URL)
        repo = RepositoryFactory.create_repository('sensor', db)
        sensors = repo.get_by_grupo(grupo)
        return sensors
    except Exception as e:
        st.error(f"Erro ao buscar sensores do grupo: {e}")
        return []

def get_aggregated_readings(sensor_ids, hours=24):
    """Obtém leituras agregadas de múltiplos sensores"""
    try:
        db = DatabaseManager(Config.DATABASE_URL)
        repo = RepositoryFactory.create_repository('reading', db)
        
        all_readings = []
        start_date = datetime.now() - timedelta(hours=hours)
        
        for sensor_id in sensor_ids:
            readings = repo.get_readings_for_sensor(sensor_id, start_date, datetime.now())
            if readings:
                for r in readings:
                    all_readings.append({
                        'sensor_id': sensor_id,
                        'timestamp': r.timestamp,
                        'value': r.value,
                        'unit': r.unit
                    })
        
        if all_readings:
            df = pd.DataFrame(all_readings)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            return df.sort_values('timestamp')
        return None
    except Exception as e:
        st.warning(f"Leituras não disponíveis: {e}")
        return None

def create_group_historical_chart(df, title):
    """Cria gráfico histórico para o grupo com múltiplas séries"""
    if df is None or df.empty:
        return None
    
    fig = go.Figure()
    
    # Adicionar uma série para cada sensor
    for sensor_id in df['sensor_id'].unique():
        sensor_data = df[df['sensor_id'] == sensor_id].sort_values('timestamp')
        
        fig.add_trace(go.Scatter(
            x=sensor_data['timestamp'],
            y=sensor_data['value'],
            mode='lines',
            name=f'Sensor {sensor_id}',
            line=dict(width=2),
            hovertemplate='<b>%{fullData.name}</b><br>%{x}<br>Valor: %{y:.2f}<extra></extra>'
        ))
    
    fig.update_layout(
        title=title,
        xaxis_title='Data/Hora',
        yaxis_title='Valor',
        template='plotly_white',
        hovermode='x unified',
        height=400,
        margin=dict(l=50, r=50, t=50, b=50)
    )
    
    return fig

def main():
    """Função principal"""
    
    # Obter grupo de votação dos session state ou query params
    if 'selected_voting_group' in st.session_state and st.session_state.selected_voting_group:
        voting_group = st.session_state.selected_voting_group
    else:
        query_params = st.query_params
        voting_group = query_params.get('voting_group', None)
    
    if not voting_group:
        st.error("❌ Nenhum grupo de votação selecionado. Por favor, clique em um grupo na tabela de monitoramento.")
        st.info("Você será redirecionado para a página de monitoramento ao voltar.")
        if st.button("← Voltar para Monitoramento", key="back_to_monitoring"):
            if 'selected_voting_group' in st.session_state:
                del st.session_state.selected_voting_group
            st.switch_page("pages/monitoring_page.py")
        return
    
    # Buscar sensores do grupo
    sensors = get_voting_group_sensors(voting_group)
    
    if not sensors:
        st.error(f"❌ Nenhum sensor encontrado no grupo '{voting_group}'.")
        st.info("Verifique o nome do grupo e tente novamente, ou volte à página de monitoramento.")
        if st.button("← Voltar para Monitoramento", key="back_error"):
            if 'selected_voting_group' in st.session_state:
                del st.session_state.selected_voting_group
            st.switch_page("pages/monitoring_page.py")
        return
    
    # Header
    st.markdown(f"""
        <div class="group-header">
            <div class="group-title">🔗 {voting_group}</div>
            <div class="group-subtitle">{len(sensors)} sensores neste grupo de votação</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Botão voltar
    col1, col2, col3 = st.columns([1, 8, 1])
    with col1:
        if st.button("← Voltar", key="back_button"):
            # Limpar session state
            if 'selected_voting_group' in st.session_state:
                del st.session_state.selected_voting_group
            st.switch_page("pages/monitoring_page.py")
    
    st.markdown("---")
    
    # Estatísticas do grupo
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="stat-box">', unsafe_allow_html=True)
        st.markdown(f'<div class="stat-number">{len(sensors)}</div>', unsafe_allow_html=True)
        st.markdown('<div class="stat-label">Total de Sensores</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        habilitados = sum(1 for s in sensors if s.enabled)
        st.markdown('<div class="stat-box">', unsafe_allow_html=True)
        st.markdown(f'<div class="stat-number">{habilitados}</div>', unsafe_allow_html=True)
        st.markdown('<div class="stat-label">Habilitados</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        # Contar tipos de gás únicos
        tipos = set(s.tipo_gas for s in sensors if s.tipo_gas and s.tipo_gas != 'N/A')
        st.markdown('<div class="stat-box">', unsafe_allow_html=True)
        st.markdown(f'<div class="stat-number">{len(tipos)}</div>', unsafe_allow_html=True)
        st.markdown('<div class="stat-label">Tipos de Gás</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        # Contar plataformas únicas
        plataformas = set(s.uep for s in sensors if s.uep and s.uep != 'N/A')
        st.markdown('<div class="stat-box">', unsafe_allow_html=True)
        st.markdown(f'<div class="stat-number">{len(plataformas)}</div>', unsafe_allow_html=True)
        st.markdown('<div class="stat-label">Plataformas</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Gráfico histórico agregado
    st.subheader("📊 Histórico Sensibilização - Grupo", divider="blue")
    
    col1, col2 = st.columns([3, 1])
    with col2:
        time_range = st.selectbox("Período:", ["24 horas", "7 dias", "30 dias"], key="time_range")
        hours = {"24 horas": 24, "7 dias": 168, "30 dias": 720}[time_range]
    
    sensor_ids = [s.sensor_id for s in sensors]
    readings_df = get_aggregated_readings(sensor_ids, hours=hours)
    
    if readings_df is not None and not readings_df.empty:
        fig = create_group_historical_chart(readings_df, f"Histórico do Grupo - {time_range}")
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("⚠️ Nenhuma leitura disponível para este período.")
    
    st.markdown("---")
    
    # Lista de sensores do grupo
    st.subheader("📋 Sensores do Grupo", divider="blue")
    
    # Agrupar por tipo de gás
    sensores_por_tipo = {}
    for sensor in sensors:
        tipo = sensor.tipo_gas or 'Não Classificado'
        if tipo not in sensores_por_tipo:
            sensores_por_tipo[tipo] = []
        sensores_por_tipo[tipo].append(sensor)
    
    # Exibir em abas por tipo de gás
    tabs = st.tabs(list(sensores_por_tipo.keys()))
    
    for tab, tipo_gas in zip(tabs, sensores_por_tipo.keys()):
        with tab:
            for sensor in sensores_por_tipo[tipo_gas]:
                with st.container(border=True):
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        st.markdown(f'<div class="sensor-name">📌 {sensor.id_af}</div>', 
                                   unsafe_allow_html=True)
                        st.markdown(f"""
                        <div class="sensor-meta">
                            <div><strong>UEP:</strong> {sensor.uep or 'N/A'}</div>
                            <div><strong>Tipo:</strong> {sensor.tipo_gas or 'N/A'}</div>
                            <div><strong>Status:</strong> {'🟢 Ativo' if sensor.enabled else '🔴 Inativo'}</div>
                        </div>
                        <small>{sensor.descricao or 'Sem descrição'}</small>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.caption("Unidade")
                        st.code(sensor.unit or 'N/A', language=None)
                    
                    with col3:
                        if st.button("Detalhes", key=f"detail_{sensor.sensor_id}"):
                            st.session_state.selected_sensor_id = sensor.id_af
                            st.switch_page("pages/sensor_detail_page.py")
    
    st.markdown("---")
    
    # Resumo de dados
    st.subheader("📊 Resumo dos Sensores", divider="blue")
    
    summary_data = []
    for sensor in sensors:
        summary_data.append({
            'TAG': sensor.id_af,
            'UEP': sensor.uep or 'N/A',
            'Tipo': sensor.tipo_gas or 'N/A',
            'Unidade': sensor.unit or 'N/A',
            'Status': '🟢 Ativo' if sensor.enabled else '🔴 Inativo',
            'Descrição': (sensor.descricao or 'N/A')[:50]
        })
    
    summary_df = pd.DataFrame(summary_data)
    st.dataframe(summary_df, use_container_width=True, hide_index=True)

if __name__ == "__main__":
    main()
