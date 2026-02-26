"""
Streamlit - Predictions Page
Página para visualização de forecasting e detecção de anomalias
"""
import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta

from src.ml.ml_engine import create_ml_engine
from src.sensors.sensor_manager import create_sensor_manager

logger = logging.getLogger(__name__)


@st.cache_resource
def get_ml_engine():
    """Cria e cacheia a instância de MLEngine"""
    return create_ml_engine()


@st.cache_resource
def get_sensor_manager():
    """Cria e cacheia a instância de SensorManager"""
    return create_sensor_manager()


def render_predictions_page():
    """Renderiza página de Predictions"""
    st.header("🔮 Predictions - ML-based Forecasting & Anomaly Detection")

    try:
        ml_engine = get_ml_engine()
        sensor_manager = get_sensor_manager()

        # Tabs principais
        tab1, tab2, tab3, tab4 = st.tabs(
            ["Forecasting", "Anomaly Detection", "Model Status", "Training"]
        )

        with tab1:
            render_forecasting_tab(ml_engine, sensor_manager)

        with tab2:
            render_anomaly_tab(ml_engine, sensor_manager)

        with tab3:
            render_model_status_tab(ml_engine, sensor_manager)

        with tab4:
            render_training_tab(ml_engine, sensor_manager)

    except Exception as e:
        logger.error(f"Erro ao renderizar Predictions: {e}")
        st.error(f"Erro ao carregar Predictions: {e}")


def render_forecasting_tab(ml_engine, sensor_manager):
    """Renderiza tab de Forecasting"""
    st.subheader("🔮 Time Series Forecasting")

    col1, col2 = st.columns([2, 1])

    with col1:
        sensors = sensor_manager.get_enabled_sensors()
        sensor_options = {s.display_name: s.sensor_id for s in sensors}

        if not sensor_options:
            st.warning("⚠️ Nenhum sensor disponível")
            return

        selected_sensor_name = st.selectbox(
            "Selecione um sensor",
            list(sensor_options.keys())
        )
        selected_sensor_id = sensor_options[selected_sensor_name]

    with col2:
        forecast_hours = st.slider(
            "Horas a prever",
            min_value=6,
            max_value=168,
            value=24,
            step=6
        )

    st.divider()

    # Realizar forecast
    try:
        with st.spinner("Realizando forecast..."):
            forecast_result = ml_engine.forecast_sensor(selected_sensor_id, forecast_hours)

        if 'error' in forecast_result:
            st.info(f"ℹ️ {forecast_result['error']}")
            return

        forecast = forecast_result.get('forecast', {})
        summary = forecast_result.get('summary', {})
        metrics = forecast_result.get('metrics', {})

        # Exibir resumo
        st.subheader("📊 Forecast Summary")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Tendência",
                summary.get('trend_direction', 'N/A')
            )

        with col2:
            st.metric(
                "Valor Médio",
                f"{summary.get('average_forecast', 0):.2f}"
            )

        with col3:
            st.metric(
                "Valor Máximo",
                f"{summary.get('max_forecast', 0):.2f}"
            )

        with col4:
            st.metric(
                "Volatilidade",
                f"{summary.get('volatility', 0):.2f}"
            )

        st.divider()

        # Gráfico de forecast
        st.subheader("📈 Forecast Chart")

        if forecast.get('timestamps') and forecast.get('forecasted_values'):
            df_forecast = pd.DataFrame({
                'Timestamp': forecast['timestamps'],
                'Forecasted': forecast['forecasted_values'],
                'Lower Bound': forecast['lower_bound'],
                'Upper Bound': forecast['upper_bound']
            })

            fig = go.Figure()

            # Linha de forecast
            fig.add_trace(go.Scatter(
                x=df_forecast['Timestamp'],
                y=df_forecast['Forecasted'],
                mode='lines',
                name='Forecast',
                line=dict(color='blue', width=2)
            ))

            # Intervalo de confiança
            fig.add_trace(go.Scatter(
                x=df_forecast['Timestamp'],
                y=df_forecast['Upper Bound'],
                fill=None,
                mode='lines',
                line_color='rgba(0,0,255,0)',
                showlegend=False
            ))

            fig.add_trace(go.Scatter(
                x=df_forecast['Timestamp'],
                y=df_forecast['Lower Bound'],
                fill='tonexty',
                mode='lines',
                line_color='rgba(0,0,255,0)',
                name='Confidence Interval (95%)',
                fillcolor='rgba(0,100,200,0.2)'
            ))

            fig.update_layout(
                title=f"Forecast: {selected_sensor_name}",
                xaxis_title="Timestamp",
                yaxis_title="Value",
                hovermode='x unified',
                height=400
            )

            st.plotly_chart(fig, use_container_width=True)

        # Métricas do modelo
        st.subheader("📊 Model Metrics")

        col1, col2, col3 = st.columns(3)

        with col1:
            mape = metrics.get('mape')
            if mape is not None:
                st.metric("MAPE", f"{mape:.2f}%")
            else:
                st.metric("MAPE", "N/A")

        with col2:
            rmse = metrics.get('rmse')
            if rmse is not None:
                st.metric("RMSE", f"{rmse:.4f}")
            else:
                st.metric("RMSE", "N/A")

        with col3:
            mae = metrics.get('mae')
            if mae is not None:
                st.metric("MAE", f"{mae:.4f}")
            else:
                st.metric("MAE", "N/A")

    except Exception as e:
        logger.error(f"Erro ao realizar forecast: {e}")
        st.error(f"Erro ao realizar forecast: {e}")


def render_anomaly_tab(ml_engine, sensor_manager):
    """Renderiza tab de Anomaly Detection"""
    st.subheader("🚨 Anomaly Detection")

    sensors = sensor_manager.get_enabled_sensors()
    sensor_options = {s.display_name: s.sensor_id for s in sensors}

    if not sensor_options:
        st.warning("⚠️ Nenhum sensor disponível")
        return

    selected_sensor_name = st.selectbox(
        "Selecione um sensor",
        list(sensor_options.keys()),
        key="anomaly_sensor"
    )
    selected_sensor_id = sensor_options[selected_sensor_name]

    st.divider()

    try:
        with st.spinner("Analisando anomalias..."):
            anomaly_result = ml_engine.detect_anomalies(selected_sensor_id)

        if 'error' in anomaly_result:
            st.info(f"ℹ️ {anomaly_result['error']}")
            return

        # Exibir resultado
        is_anomaly = anomaly_result.get('is_anomaly', False)
        anomaly_score = anomaly_result.get('anomaly_score', 0)
        current_value = anomaly_result.get('value', 0)
        historical_avg = anomaly_result.get('historical_average', 0)
        historical_std = anomaly_result.get('historical_std', 0)

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            status = "🚨 ANOMALIA" if is_anomaly else "✓ Normal"
            st.metric("Status", status)

        with col2:
            st.metric("Score", f"{anomaly_score:.4f}")

        with col3:
            st.metric("Valor Atual", f"{current_value:.2f}")

        with col4:
            diff_percent = ((current_value - historical_avg) / historical_avg * 100) if historical_avg != 0 else 0
            st.metric("Desvio %", f"{diff_percent:+.1f}%")

        st.divider()

        # Gráfico de histórico com detecção
        st.subheader("📈 Historical Data with Anomalies")

        # Recuperar histórico
        timestamps, values = ml_engine.get_sensor_history(selected_sensor_id, hours=72)

        if timestamps and values:
            df_history = pd.DataFrame({
                'Timestamp': timestamps,
                'Value': values
            })

            # Detectar anomalias para todo o histórico
            predictions, scores = ml_engine.anomaly_detectors[selected_sensor_id].detect_ensemble(
                np.array(values)
            ) if selected_sensor_id in ml_engine.anomaly_detectors else ([], [])

            if predictions:
                df_history['Anomaly'] = ['Anomalia' if p == -1 else 'Normal' for p in predictions]
                df_history['Score'] = scores

                fig = go.Figure()

                # Valores normais
                normal_mask = df_history['Anomaly'] == 'Normal'
                fig.add_trace(go.Scatter(
                    x=df_history[normal_mask]['Timestamp'],
                    y=df_history[normal_mask]['Value'],
                    mode='lines+markers',
                    name='Normal',
                    line=dict(color='green')
                ))

                # Anomalias
                anomaly_mask = df_history['Anomaly'] == 'Anomalia'
                if anomaly_mask.any():
                    fig.add_trace(go.Scatter(
                        x=df_history[anomaly_mask]['Timestamp'],
                        y=df_history[anomaly_mask]['Value'],
                        mode='markers',
                        name='Anomalias',
                        marker=dict(color='red', size=10)
                    ))

                # Linhas de referência
                fig.add_hline(y=historical_avg, line_dash="dash", line_color="blue",
                             annotation_text="Média Histórica")
                fig.add_hline(y=historical_avg + historical_std, line_dash="dot",
                             line_color="orange", annotation_text="±σ")
                fig.add_hline(y=historical_avg - historical_std, line_dash="dot",
                             line_color="orange")

                fig.update_layout(
                    title=f"Anomaly Detection: {selected_sensor_name}",
                    xaxis_title="Timestamp",
                    yaxis_title="Value",
                    hovermode='x unified',
                    height=400
                )

                st.plotly_chart(fig, use_container_width=True)

            else:
                st.info("ℹ️ Modelo não treinado. Treine o modelo na aba Training.")

    except Exception as e:
        logger.error(f"Erro ao detectar anomalias: {e}")
        st.error(f"Erro ao detectar anomalias: {e}")


def render_model_status_tab(ml_engine, sensor_manager):
    """Renderiza tab de Model Status"""
    st.subheader("🔧 Model Training Status")

    status = ml_engine.get_ml_status()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Anomaly Detectors", f"{status['anomaly_detectors_trained']}/{status['total_sensors']}")
        st.markdown(f"Cobertura: {status['coverage_anomaly']}")

    with col2:
        st.metric("Forecasters", f"{status['forecasters_trained']}/{status['total_sensors']}")
        st.markdown(f"Cobertura: {status['coverage_forecaster']}")

    with col3:
        st.metric("Total Sensors", status['total_sensors'])
        st.markdown(f"Última atualização: {status['timestamp'].strftime('%H:%M:%S')}")

    st.divider()

    # Detalhes por sensor
    st.subheader("📊 Sensors Training Details")

    sensors = sensor_manager.get_enabled_sensors()

    if sensors:
        data = []
        for sensor in sensors:
            has_anomaly = sensor.sensor_id in ml_engine.anomaly_detectors
            has_forecast = sensor.sensor_id in ml_engine.forecasters

            data.append({
                'Sensor': sensor.display_name,
                'Platform': sensor.platform,
                'Type': sensor.sensor_type,
                'Anomaly Detector': '✓' if has_anomaly else '✗',
                'Forecaster': '✓' if has_forecast else '✗'
            })

        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Nenhum sensor disponível")


def render_training_tab(ml_engine, sensor_manager):
    """Renderiza tab de Training"""
    st.subheader("🎯 Model Training")

    sensors = sensor_manager.get_enabled_sensors()

    if not sensors:
        st.warning("⚠️ Nenhum sensor disponível para treino")
        return

    sensor_options = {s.display_name: s.sensor_id for s in sensors}

    col1, col2 = st.columns([2, 1])

    with col1:
        selected_sensors = st.multiselect(
            "Selecione sensores para treino",
            list(sensor_options.keys()),
            default=list(sensor_options.keys())[:3]
        )

    with col2:
        if st.button("🚀 Treinar Modelos", type="primary"):
            training_progress = st.progress(0)
            status_text = st.empty()

            selected_ids = [sensor_options[name] for name in selected_sensors]

            # Treinar anomaly detectors
            trained_anomaly = 0
            for idx, sensor_id in enumerate(selected_ids):
                status_text.text(f"Treinando Anomaly Detector {idx + 1}/{len(selected_ids)}...")
                if ml_engine.train_anomaly_detector(sensor_id):
                    trained_anomaly += 1
                training_progress.progress((idx + 1) / (len(selected_ids) * 2))

            # Treinar forecasters
            trained_forecaster = 0
            for idx, sensor_id in enumerate(selected_ids):
                status_text.text(f"Treinando Forecaster {idx + 1}/{len(selected_ids)}...")
                if ml_engine.train_forecaster(sensor_id):
                    trained_forecaster += 1
                training_progress.progress(0.5 + (idx + 1) / (len(selected_ids) * 2))

            training_progress.progress(1.0)
            st.success(f"✓ Treino concluído!\n- Anomaly Detectors: {trained_anomaly}/{len(selected_ids)}\n- Forecasters: {trained_forecaster}/{len(selected_ids)}")

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📋 Training Requirements")
        st.markdown("""
        **Dados Necessários:**
        - Anomaly Detector: mínimo 30 leituras
        - Forecaster: mínimo 50 leituras
        
        **Qualidade dos Dados:**
        - Apenas leituras com data_quality = 0
        - Timestamps válidos e únicos
        """)

    with col2:
        st.subheader("📊 Training Tips")
        st.markdown("""
        **Melhorar Precisão:**
        - Coletar mais dados históricos
        - Garantir dados de boa qualidade
        - Treinar periodicamente (daily/weekly)
        - Usar dados sazonais quando possível
        """)


if __name__ == "__main__":
    render_predictions_page()
