"""
SafePlan Control Hub - Interface de Configuração e Gerenciamento

Uma interface gráfica intuitiva para:
- Configurar credenciais
- Inicializar banco de dados
- Descobrir e importar sensores
- Visitar dashboard de monitoramento
"""

import streamlit as st
import subprocess
import sys
import os
from pathlib import Path
import json
import time
from datetime import datetime

# Config
st.set_page_config(
    page_title="SafePlan Control Hub",
    page_icon="🎛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Paths
PROJECT_ROOT = Path(__file__).parent
ENV_FILE = PROJECT_ROOT / '.env'
JSON_FILE = PROJECT_ROOT / 'config' / 'sensor_paths_buzios.json'

# CSS customizado
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] button {
        font-size: 18px;
        font-weight: bold;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 4px;
        padding: 20px;
        color: #155724;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 4px;
        padding: 20px;
        color: #721c24;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 4px;
        padding: 20px;
        color: #0c5460;
    }
    </style>
""", unsafe_allow_html=True)

# Funções auxiliares
def run_script(script_name: str, args: list = None) -> tuple[bool, str]:
    """Executa um script Python e retorna (sucesso, output)."""
    try:
        cmd = [sys.executable, f"scripts/{script_name}"] + (args or [])
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
            timeout=300
        )
        return result.returncode == 0, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return False, "Timeout: operação levou muito tempo"
    except Exception as e:
        return False, f"Erro: {str(e)}"

def check_env_configured() -> bool:
    """Verifica se .env está configurado."""
    if not ENV_FILE.exists():
        return False
    
    with open(ENV_FILE, 'r') as f:
        content = f.read()
        return 'PI_SERVER_USERNAME=' in content and 'PI_SERVER_PASSWORD=' in content

def check_sensores_discovered() -> int:
    """Verifica quantos sensores foram descobertos."""
    if not JSON_FILE.exists():
        return 0
    
    try:
        with open(JSON_FILE, 'r') as f:
            data = json.load(f)
            return len(data.get('sensors', []))
    except:
        return 0

def check_db_initialized() -> bool:
    """Verifica se banco foi inicializado."""
    db_file = PROJECT_ROOT / 'safeplan.db'
    return db_file.exists()

# Layout
st.title("🎛️ SafePlan Control Hub")
st.subheader("Painel de Controle para Configuração e Gerenciamento")

# Sidebar com status
with st.sidebar:
    st.header("📊 Status do Projeto")
    
    col1, col2 = st.columns(2)
    with col1:
        if check_env_configured():
            st.success("✓ Credenciais")
        else:
            st.error("✗ Credenciais")
    
    with col2:
        if check_db_initialized():
            st.success("✓ Banco de Dados")
        else:
            st.error("✗ Banco de Dados")
    
    sensores_count = check_sensores_discovered()
    if sensores_count > 0:
        st.success(f"✓ {sensores_count} Sensores")
    else:
        st.warning("⚠ Sem sensores")
    
    st.divider()
    
    if st.button("🚀 Abrir Dashboard", use_container_width=True, key="dash_btn"):
        st.info("Use em outro terminal: `streamlit run app/main.py`")

# Tabs principais
tabs = st.tabs([
    "🚀 Quick Start",
    "🔐 Credenciais",
    "🗄️ Banco de Dados",
    "📡 Sensores",
    "❓ Ajuda"
])

# TAB 1: Quick Start
with tabs[0]:
    st.header("⚡ Início Rápido em 5 Passos")
    
    steps = [
        ("1️⃣ Configurar Credenciais", "Detecta seu username Windows e solicita senha"),
        ("2️⃣ Inicializar Banco", "Cria estrutura do banco de dados"),
        ("3️⃣ Descobrir Sensores", "Busca sensores do PI AF ou modo DEMO"),
        ("4️⃣ Importar Sensores", "Importa para o banco de dados"),
        ("5️⃣ Gerar Dados Teste", "Popula leituras de exemplo (opcional)"),
    ]
    
    for step, desc in steps:
        st.write(f"**{step}**")
        st.write(f"_{desc}_")
        st.write("")
    
    st.divider()
    
    if st.button("▶️ Executar Todos os Passos", use_container_width=True, key="quick_start"):
        with st.spinner("Processando..."):
            steps_to_run = [
                ("1️⃣ Configurando credenciais...", "setup_credentials.py", []),
                ("2️⃣ Inicializando banco...", "init_db.py", []),
                ("3️⃣ Descobrindo sensores...", "discover_sensors_from_af.py", ["--demo"]),
                ("4️⃣ Importando sensores...", "import_sensors_from_buzios.py", []),
                ("5️⃣ Gerando dados de teste...", "create_sample_data.py", []),
            ]
            
            for label, script, args in steps_to_run:
                st.write(label)
                success, output = run_script(script, args)
                
                if success:
                    st.success("✓ Concluído")
                else:
                    st.error(f"✗ Erro: {output[:200]}")
                    break
                time.sleep(0.5)
            
            if success:
                st.success("✅ Todos os passos completados!")
                st.info("Próximo: Abra o dashboard em `streamlit run app/main.py`")

# TAB 2: Credenciais
with tabs[1]:
    st.header("🔐 Configuração de Credenciais")
    
    st.write("Configure as credenciais do PI Server de forma segura.")
    st.write("")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if check_env_configured():
            st.success("✅ Credenciais ja configuradas")
        else:
            st.warning("⚠️ Credenciais não configuradas")
    
    with col2:
        if st.button("🔧 Configurar Agora", use_container_width=True, key="setup_creds"):
            with st.spinner("Abrindo configurador..."):
                success, output = run_script("setup_credentials.py")
                
                if success:
                    st.success("✅ Credenciais configuradas com sucesso!")
                else:
                    st.error(f"Erro: {output}")
    
    st.divider()
    st.info("""
    **O configurador irá:**
    - 🔍 Detectar automaticamente seu username Windows
    - 🔑 Solicitar sua senha do PI Server
    - ✅ Validar a configuração
    - 💾 Salvar no .env de forma segura
    """)

# TAB 3: Banco de Dados
with tabs[2]:
    st.header("🗄️ Banco de Dados")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Status")
        if check_db_initialized():
            st.success("✅ Banco inicializado")
        else:
            st.error("❌ Banco não inicializado")
    
    with col2:
        st.subheader("Ações")
        if st.button("🔧 Inicializar Banco", use_container_width=True, key="init_db"):
            with st.spinner("Inicializando..."):
                success, output = run_script("init_db.py")
                
                if success:
                    st.success("✅ Banco inicializado!")
                else:
                    st.error(f"Erro: {output}")
    
    st.divider()
    st.info("""
    Cria a estrutura do banco de dados com as seguintes tabelas:
    - SensorConfig: Configuração dos sensores
    - Reading: Leituras dos sensores
    - Alert: Alertas gerados
    - AlertRule: Regras de alerta
    """)

# TAB 4: Sensores
with tabs[3]:
    st.header("📡 Gerenciamento de Sensores")
    
    subtabs = st.tabs(["Descobrir", "Importar", "Status"])
    
    with subtabs[0]:
        st.subheader("Descobrir Sensores do PI AF")
        
        col1, col2 = st.columns(2)
        
        with col1:
            mode = st.radio(
                "Modo de Descoberta",
                ["PI AF Real (Requer acesso)", "DEMO (Sem conexão)"],
                index=1
            )
        
        with col2:
            if st.button("🔍 Descobrir Sensores", use_container_width=True):
                with st.spinner("Descobrindo sensores..."):
                    args = [] if mode.startswith("PI AF") else ["--demo"]
                    success, output = run_script("discover_sensors_from_af.py", args)
                    
                    if success:
                        sensores = check_sensores_discovered()
                        st.success(f"✅ {sensores} sensores descobertos!")
                    else:
                        st.error(f"Erro: {output[:500]}")
    
    with subtabs[1]:
        st.subheader("Importar Sensores para Banco")
        
        if st.button("📥 Importar Sensores", use_container_width=True):
            with st.spinner("Importando..."):
                success, output = run_script("import_sensors_from_buzios.py")
                
                if success:
                    st.success("✅ Sensores importados!")
                else:
                    st.error(f"Erro: {output[:500]}")
    
    with subtabs[2]:
        st.subheader("Status dos Sensores")
        
        sensores = check_sensores_discovered()
        db_init = check_db_initialized()
        
        st.metric("Sensores Descobertos", sensores if sensores > 0 else "Nenhum")
        st.metric("Banco de Dados", "✅ Inicializado" if db_init else "❌ Não inicializado")

# TAB 5: Ajuda
with tabs[4]:
    st.header("❓ Ajuda e Documentação")
    
    with st.expander("📖 Qual é o fluxo recomendado?", expanded=True):
        st.write("""
        1. **Configurar Credenciais** → setup_credentials.py
           - Detecta seu username Windows
           - Solicita senha de forma segura
        
        2. **Inicializar Banco** → init_db.py
           - Cria tabelas no banco de dados
        
        3. **Descobrir Sensores** → discover_sensors_from_af.py
           - Conecta ao PI AF (real ou demo)
           - Extrai 10 atributos de cada sensor
        
        4. **Importar Sensores** → import_sensors_from_buzios.py
           - Importa para o banco de dados
           - Configura thresholds padrão
        
        5. **Dashboard** → streamlit run app/main.py
           - Visualiza sensores em tempo real
        """)
    
    with st.expander("🆘 O que fazer se houver erro?"):
        st.write("""
        **Erro: "Python não encontrado"**
        - Instale Python 3.10+ de https://python.org
        - Marque "Add Python to PATH"
        
        **Erro: "Falha ao conectar ao PI AF"**
        - Verifique credenciais no .env
        - Verifique acesso à rede
        - Use modo DEMO para testar
        
        **Erro: "Banco de dados bloqueado"**
        - Feche o dashboard (streamlit)
        - Tente novamente
        """)
    
    with st.expander("📚 Scripts Disponíveis"):
        scripts_info = {
            "setup_credentials.py": "Configura credenciais com username Windows automático",
            "init_db.py": "Inicializa estrutura do banco de dados",
            "discover_sensors_from_af.py": "Descobre sensores (real ou demo)",
            "import_sensors_from_buzios.py": "Importa sensores para banco",
            "create_sample_data.py": "Gera dados de teste",
            "test_af_connectivity.py": "Testa conexão com PI AF",
        }
        
        for script, desc in scripts_info.items():
            st.write(f"**{script}**")
            st.write(f"_{desc}_")
            st.write("")
    
    with st.expander("🔗 Links Úteis"):
        st.write("- [Documentação SafePlan](README.md)")
        st.write("- [Guia de Início Rápido](GETTING_STARTED.md)")
        st.write("- [PI Server Documentation](https://pi-af-sdk.readthedocs.io/)")

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: gray; margin-top: 50px;">
    <p>SafePlan © 2026 - Plataforma de Monitoramento de Sensores de Fogo e Gás</p>
    <p>Para abrir o Dashboard de Monitoramento: <code>streamlit run app/main.py</code></p>
</div>
""", unsafe_allow_html=True)
