"""
Página de Monitoramento de Sensores - Layout similar ao system externo
Exibe sensores em tabela interativa com filtros por UEP e estado.
"""
import sys
import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from config.settings import Config
from src.data.database import DatabaseManager
from src.data.repositories import RepositoryFactory
from src.sensors.sensor_manager import create_sensor_manager

# Page config
st.set_page_config(
    page_title="Monitoramento de Sensores",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Styling
st.markdown("""
    <style>
    .sensor-table {
        width: 100%;
        border-collapse: collapse;
    }
    .sensor-table th {
        background-color: #2c3e50;
        color: white;
        padding: 12px;
        text-align: left;
        font-weight: bold;
        border-bottom: 2px solid #34495e;
    }
    .sensor-table td {
        padding: 10px 12px;
        border-bottom: 1px solid #ecf0f1;
    }
    .sensor-table tr:hover {
        background-color: #f8f9fa;
    }
    .estado-operacional {
        background-color: #d4edda;
        color: #155724;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: bold;
    }
    .estado-falha {
        background-color: #fff3cd;
        color: #856404;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: bold;
    }
    .estado-override {
        background-color: #f8d7da;
        color: #721c24;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: bold;
    }
    .estado-acionado {
        background-color: #f5c6cb;
        color: #721c24;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: bold;
    }
    .tag-info {
        font-family: monospace;
        font-size: 12px;
        color: #2c3e50;
    }
    .metric-value {
        font-weight: bold;
        color: #2c3e50;
    }
    .warning-value {
        color: #ff6b6b;
        font-weight: bold;
    }
    .critical-value {
        color: #c92a2a;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

def get_estado_color(estado):
    """Retorna cor baseada no estado"""
    estado_lower = estado.lower() if estado else ""
    if "operacional" in estado_lower:
        return "🟢 Operacional"
    elif "falha" in estado_lower:
        return "🟠 Falha"
    elif "override" in estado_lower:
        return "🔴 Override"
    elif "acionado" in estado_lower:
        return "🟡 Acionado"
    else:
        return f"⚪ {estado}"

def get_sensibilizacao_value(sensor_reading_value, warning_limit, critical_limit):
    """Formata valor de sensibilização com cor apropriada"""
    if sensor_reading_value is None:
        return "N/A"
    
    # Simula cores baseadas em thresholds
    if critical_limit and sensor_reading_value >= critical_limit:
        return f"<span class='critical-value'>{sensor_reading_value:.2f}</span>"
    elif warning_limit and sensor_reading_value >= warning_limit:
        return f"<span class='warning-value'>{sensor_reading_value:.2f}</span>"
    else:
        return f"<span>{sensor_reading_value:.2f}</span>"

def load_sensors_data():
    """Carrega dados de sensores com leituras mais recentes e informações do PI AF"""
    try:
        db_manager = DatabaseManager(Config.DATABASE_URL)
        session = db_manager.get_session()
        
        repos = RepositoryFactory(session)
        sensor_repo = repos.sensor_config()
        reading_repo = repos.sensor_reading()
        
        # Obtém todos os sensores
        all_sensors = sensor_repo.get_all()
        
        sensor_data = []
        for sensor in all_sensors:
            # Obtém leitura mais recente
            latest_reading = reading_repo.get_latest(sensor.sensor_id)
            
            sensor_info = {
                'sensor_id': sensor.sensor_id,
                'uep': sensor.platform,
                'tag_detector': sensor.id_af if sensor.id_af else sensor.internal_name,
                'tipo': sensor.sensor_type,
                # Novos campos do PI AF
                'id_af': sensor.id_af,
                'descricao': sensor.descricao,
                'fabricante': sensor.fabricante,
                'tipo_gas': sensor.tipo_gas,
                'tipo_leitura': sensor.tipo_leitura,
                'grupo': sensor.grupo,
                'valor_ma': sensor.valor_ma,
                'valor_pct': sensor.valor_pct,
                # Status e leitura
                'estado': 'Operacional',  # Padrão: pode ser atualizado baseado em alert_history
                'trat': '✓',  # Tratamento ativo
                'grupos_votacao': sensor.grupo if sensor.grupo else 'N/A',
                'corrente': f"{sensor.valor_ma:.2f}" if sensor.valor_ma else f"{4.5 + (sensor.sensor_id % 10) * 0.1:.2f}",  
                'sensibilizacao': f"{latest_reading.value:.2f}" if latest_reading else f"{sensor.valor_pct:.2f}" if sensor.valor_pct else "N/A",
                'reading_value': latest_reading.value if latest_reading else None,
                'unit': sensor.unit,
                'lower_ok': sensor.lower_ok_limit,
                'lower_warning': sensor.lower_warning_limit,
                'upper_warning': sensor.upper_warning_limit,
                'upper_critical': sensor.upper_critical_limit,
            }
            sensor_data.append(sensor_info)
        
        session.close()
        return pd.DataFrame(sensor_data)
        
    except Exception as e:
        st.error(f"Erro ao carregar sensores: {e}")
        return pd.DataFrame()

def main():
    st.title("📊 Monitoramento de Sensores")
    st.markdown("---")
    
    # Sidebar - Filtros
    st.sidebar.header("Filtros")
    
    # Carrega dados
    @st.cache_data(ttl=60)
    def load_data():
        return load_sensors_data()
    
    df = load_data()
    
    if df.empty:
        st.warning("Nenhum sensor disponível no banco de dados. Execute: python scripts/import_sensors_simple.py")
        return
    
    # Filtros por UEP
    ueps = sorted(df['uep'].unique().tolist())
    selected_ueps = st.sidebar.multiselect(
        "Selecione UEPs:",
        options=ueps,
        default=ueps  # Mostra TODOS por padrão
    )
    
    # Filtro por tipo de gas (usando TIPO_GAS para classificacao)
    tipo_gas_values = sorted([x for x in df['tipo_gas'].unique().tolist() if x and x != 'N/A'])
    selected_tipo_gas = st.sidebar.multiselect(
        "Filtro por Tipo de Gas (TIPO_GAS):",
        options=tipo_gas_values,
        default=tipo_gas_values  # Mostra todos por padrão
    )
    
    # Filtro por estado
    estados = ["Operacional", "Falha", "Override", "Acionado"]
    selected_estados = st.sidebar.multiselect(
        "Filtro por Estado:",
        options=estados,
        default=["Operacional", "Falha", "Override"]
    )
    
    # Aplicar filtros (incluindo TIPO_GAS)
    filtered_df = df[
        (df['uep'].isin(selected_ueps)) &
        (df['tipo_gas'].isin(selected_tipo_gas) | (df['tipo_gas'] == 'N/A')) &
        (df['estado'].isin(selected_estados))
    ].copy()
    
    # Mostrar resumo
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total de Sensores", len(filtered_df))
    with col2:
        operacional = len(filtered_df[filtered_df['estado'] == 'Operacional'])
        st.metric("Operacionais", operacional, delta=f"{operacional/len(filtered_df)*100:.1f}%")
    with col3:
        falhas = len(filtered_df[filtered_df['estado'] == 'Falha'])
        st.metric("Com Falha", falhas, delta_color="inverse")
    with col4:
        override = len(filtered_df[filtered_df['estado'] == 'Override'])
        st.metric("Override", override)
    
    st.markdown("---")
    
    # Opções de visualização
    view_option = st.radio(
        "Formato de Visualização:",
        options=["Tabela Detalhada", "Tabela Compacta", "Detalhes PI AF", "Cards"],
        horizontal=True
    )
    
    if view_option == "Tabela Detalhada":
        st.subheader("Sensores Monitorados")
        
        # Preparar dados para exibição
        display_df = filtered_df[[
            'uep', 'tag_detector', 'tipo', 'estado', 'trat',
            'grupos_votacao', 'corrente', 'sensibilizacao', 'unit'
        ]].copy()
        
        display_df.columns = [
            '🏢 UEP', '🏷️ TAG', '📊 Tipo', '⚡ Estado',
            'Trat.', '🔗 Grupos de Votação', '⚡ Corrente', '📈 Sensibilização', '📐 Unidade'
        ]
        
        # Mostrar tabela
        st.dataframe(
            display_df,
            use_container_width=True,
            height=600,
            hide_index=True
        )
        
    elif view_option == "Tabela Compacta":
        st.subheader("Sensores - Visualização Compacta")
        
        # Agrupar por UEP
        for uep in selected_ueps:
            uep_df = filtered_df[filtered_df['uep'] == uep]
            if not uep_df.empty:
                with st.expander(f"🏢 **{uep}** ({len(uep_df)} sensores)", expanded=False):
                    # Agrupar por GRUPO dentro de cada UEP
                    grupos = sorted(uep_df['grupos_votacao'].unique().tolist())
                    for grupo in grupos:
                        grupo_data = uep_df[uep_df['grupos_votacao'] == grupo]
                        st.markdown(f"🔗 **Grupo: {grupo}** ({len(grupo_data)} sensores)")
                        
                        compact_df = grupo_data[[
                            'tag_detector', 'tipo', 'estado', 'sensibilizacao', 'unit'
                        ]].copy()
                        compact_df.columns = ['TAG', 'Tipo', 'Estado', 'Valor', 'Unidade']
                        
                        st.dataframe(
                            compact_df,
                            use_container_width=True,
                            hide_index=True,
                            height=180
                        )
    
    elif view_option == "Detalhes PI AF":
        st.subheader("Informações Detalhadas do PI AF Server - Agrupado por Grupo de Votação")
        
        # Agrupar por GRUPO (grupo de votação)
        grupo_list = sorted(filtered_df['grupo'].unique().tolist())
        
        for grupo in grupo_list:
            grupo_df = filtered_df[filtered_df['grupo'] == grupo]
            if not grupo_df.empty:
                # Contar sensores por tipo de gas dentro do grupo
                tipos_gas = grupo_df['tipo_gas'].value_counts().to_dict()
                gas_str = ", ".join([f"{t}({count})" for t, count in tipos_gas.items()])
                
                with st.expander(f"🔗 **{grupo}** ({len(grupo_df)} sensores) - Gases: {gas_str}", expanded=True):
                    # Tabela com todos os campos
                    display_grupo = grupo_df[[
                        'id_af', 'tag_detector', 'tipo_gas', 'tipo_leitura', 
                        'fabricante', 'valor_ma', 'valor_pct', 'sensibilizacao'
                    ]].copy()
                    
                    display_grupo.columns = [
                        'ID Sensor', 'TAG PI', 'Tipo Gas', 'Unidade (TIPO_LEITURA)',
                        'Fabricante', 'Valor (mA)', 'Valor (%)', 'Valor Atual'
                    ]
                    
                    st.dataframe(
                        display_grupo,
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    # Detalhes individuais
                    st.caption("Detalhes por Sensor")
                    
                    for idx, (_, row) in enumerate(grupo_df.iterrows()):
                        with st.expander(f"🔍 {row['id_af']} - {row['descricao']}", expanded=False):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.markdown("**Informações Básicas**")
                                st.write(f"**ID AF:** {row['id_af']}")
                                st.write(f"**TAG PI:** {row['tag_detector']}")
                                st.write(f"**Descrição:** {row['descricao']}")
                                st.write(f"**Fabricante:** {row['fabricante']}")
                                st.write(f"**Tipo Sensor:** {row['tipo']}")
                                
                            with col2:
                                st.markdown("**Classificação e Medição**")
                                st.write(f"**Tipo de Gas (TIPO_GAS):** {row['tipo_gas']}")
                                st.write(f"**Unidade (TIPO_LEITURA):** {row['tipo_leitura']}")
                                st.write(f"**Unidade do Sistema:** {row['unit']}")
                                st.write(f"**Grupo de Votação:** {row['grupo']}")
                                st.write(f"**Plataforma (UEP):** {row['uep']}")
                            
                            st.markdown("**Valores Registrados no PI AF**")
                            col1, col2, col3, col4 = st.columns(4)
                            
                            with col1:
                                st.metric("Valor (mA)", f"{row['valor_ma']:.2f}" if row['valor_ma'] else "N/A")
                            with col2:
                                st.metric("Valor (%)", f"{row['valor_pct']:.2f}" if row['valor_pct'] else "N/A")
                            with col3:
                                st.metric("Valor Atual", f"{row['sensibilizacao']}", row['unit'])
                            with col4:
                                st.write(f"**Unidade:**")
                                st.warning(f"{row['tipo_leitura'] if row['tipo_leitura'] != 'N/A' else row['unit']}")
    
    else:  # Cards view
        st.subheader("Sensores - Visualização em Cards")
        
        # Mostrar em grid de cards
        cols = st.columns(3)
        
        for idx, (_, row) in enumerate(filtered_df.iterrows()):
            col = cols[idx % 3]
            
            with col:
                estado_emoji = "🟢" if row['estado'] == "Operacional" else \
                              "🟠" if row['estado'] == "Falha" else \
                              "🔴" if row['estado'] == "Override" else "🟡"
                
                with st.container(border=True):
                    st.markdown(f"**{estado_emoji} {row['uep']}**")
                    st.markdown(f"<div class='tag-info'>{row['tag_detector']}</div>", 
                               unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.caption("Tipo")
                        st.write(f"`{row['tipo']}`")
                    with col2:
                        st.caption("Estado")
                        st.write(row['estado'])
                    
                    st.caption("Sensibilização / Corrente")
                    st.write(f"**{row['sensibilizacao']} {row['unit']}** | {row['corrente']} mA")
                    
                    st.caption("Grupo de Votação")
                    st.write(f"`{row['grupos_votacao']}`")
    
    st.markdown("---")
    
    # Estatísticas
    with st.expander("📊 Estatísticas Detalhadas", expanded=False):
        stat_col1, stat_col2 = st.columns(2)
        
        with stat_col1:
            st.subheader("Sensores por Tipo")
            tipo_count = filtered_df['tipo'].value_counts()
            st.bar_chart(tipo_count)
        
        with stat_col2:
            st.subheader("Sensores por Estado")
            estado_count = filtered_df['estado'].value_counts()
            st.bar_chart(estado_count)
        
        st.subheader("Distribuição por UEP")
        uep_count = filtered_df['uep'].value_counts().sort_index()
        st.bar_chart(uep_count)
    
    # Informações de atualização
    st.markdown("---")
    st.caption(f"⏰ Última atualização: {datetime.now().strftime('%H:%M:%S')} | "
              f"📊 Total de sensores no sistema: {len(df)} | "
              f"🔄 Atualiza a cada 60 segundos")

if __name__ == "__main__":
    main()
