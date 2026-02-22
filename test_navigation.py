"""
Test simple para verificar se as páginas funcionam sem erros
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    print("✓ Importando monitoring_page...")
    from app.pages.monitoring_page import main as monitoring_main
    print("  OK")
    
    print("✓ Importando sensor_detail_page...")
    from app.pages.sensor_detail_page import main as sensor_main
    print("  OK")
    
    print("✓ Importando voting_group_detail_page...")
    from app.pages.voting_group_detail_page import main as group_main
    print("  OK")
    
    print("✓ Importando repositories...")
    from src.data.repositories import RepositoryFactory, SensorConfigRepository
    print("  OK")
    
    print("\n✅ TODOS OS IMPORTS OK!")
    print("\nPróxima ação:")
    print("  1. Execute: streamlit run app/main.py")
    print("  2. Abra: http://localhost:8501/monitoring_page")
    print("  3. Clique em qualquer TAG ou Grupo para navegar")
    
except Exception as e:
    print(f"\n❌ ERRO: {e}")
    import traceback
    traceback.print_exc()
