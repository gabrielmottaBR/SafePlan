"""
SafePlan Launcher
Runs the Streamlit app with proper Python path
"""
import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Set environment variable
os.environ['PYTHONPATH'] = project_root

# Run streamlit
import streamlit.cli as stcli

sys.argv = ['streamlit', 'run', 'app/main.py', '--server.port=8501']
stcli.main()
