#!/usr/bin/env python3
"""
Exemplos de uso dos novos campos Grupo e Módulo
Demonstração das queries disponíveis no SensorConfigRepository
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.src.data.models import SensorConfig
from backend.src.data.sensor_repository import SensorConfigRepository


def main():
    # Initialize database connection
    engine = create_engine('sqlite:///backend/safeplan.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Create repository
    repo = SensorConfigRepository(session)
    
    print("\n" + "="*80)
    print("SafePlan - Exemplos de Uso: Grupo e Módulo")
    print("="*80 + "\n")
    
    # ============================================================
    # 1. Listar todos os grupos únicos
    # ============================================================
    print("[1] LISTAR TODOS OS GRUPOS")
    print("-" * 80)
    
    grupos = repo.get_grupos()
    print(f"Total de grupos: {len(grupos)}\n")
    print("Grupos (primeiros 15):")
    for grupo in grupos[:15]:
        count = repo.count_by_grupo().get(grupo, 0)
        print(f"  • {grupo:20s} - {count:5d} sensores")
    print()
    
    # ============================================================
    # 2. Listar todos os módulos únicos
    # ============================================================
    print("[2] LISTAR TODOS OS MÓDULOS")
    print("-" * 80)
    
    modulos = repo.get_modulos()
    print(f"Total de módulos: {len(modulos)}\n")
    print("Módulos (primeiros 15):")
    for modulo in modulos[:15]:
        count = repo.count_by_modulo().get(modulo, 0)
        print(f"  • {modulo:20s} - {count:5d} sensores")
    print()
    
    # ============================================================
    # 3. Sensores de um grupo específico
    # ============================================================
    print("[3] SENSORES DE UM GRUPO ESPECÍFICO")
    print("-" * 80)
    
    grupo_exemplo = "10S_FD"
    sensores_grupo = repo.get_by_grupo(grupo_exemplo, limit=5)
    print(f"Grupo: {grupo_exemplo}")
    print(f"Total: {len(repo.get_by_grupo(grupo_exemplo, skip=0, limit=10000))} sensores\n")
    print("Amostras:")
    for sensor in sensores_grupo:
        print(f"  • {sensor.sensor_id:20s} | {sensor.name:40s} | Módulo: {sensor.modulo}")
    print()
    
    # ============================================================
    # 4. Sensores de um módulo específico
    # ============================================================
    print("[4] SENSORES DE UM MÓDULO ESPECÍFICO")
    print("-" * 80)
    
    modulo_exemplo = "HULL"
    sensores_modulo = repo.get_by_modulo(modulo_exemplo, limit=5)
    print(f"Módulo: {modulo_exemplo}")
    print(f"Total: {len(repo.get_by_modulo(modulo_exemplo, skip=0, limit=10000))} sensores\n")
    print("Amostras:")
    for sensor in sensores_modulo:
        print(f"  • {sensor.sensor_id:20s} | {sensor.name:40s} | Grupo: {sensor.grupo}")
    print()
    
    # ============================================================
    # 5. Análise: Distribuição de tipos por módulo
    # ============================================================
    print("[5] ANÁLISE: DISTRIBUIÇÃO DE TIPOS POR MÓDULO")
    print("-" * 80)
    
    modulo_exemplo = "M05"
    sensores = repo.get_by_modulo(modulo_exemplo, limit=10000)
    
    tipos_count = {}
    for sensor in sensores:
        tipo = sensor.sensor_type
        tipos_count[tipo] = tipos_count.get(tipo, 0) + 1
    
    print(f"Módulo: {modulo_exemplo}")
    print(f"Total de sensores: {len(sensores)}\n")
    print("Distribuição por tipo:")
    for tipo, count in sorted(tipos_count.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(sensores)) * 100
        print(f"  • {tipo:20s} - {count:4d} ({percentage:5.1f}%)")
    print()
    
    # ============================================================
    # 6. Análise: Grupos em um módulo
    # ============================================================
    print("[6] ANÁLISE: GRUPOS DENTRO DE UM MÓDULO")
    print("-" * 80)
    
    modulo_exemplo = "M10"
    sensores = repo.get_by_modulo(modulo_exemplo, limit=10000)
    
    grupos_count = {}
    for sensor in sensores:
        if sensor.grupo:
            grupos_count[sensor.grupo] = grupos_count.get(sensor.grupo, 0) + 1
    
    print(f"Módulo: {modulo_exemplo}")
    print(f"Total de sensores: {len(sensores)}")
    print(f"Unique grupos: {len(grupos_count)}\n")
    print("Grupos no módulo:")
    for grupo, count in sorted(grupos_count.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(sensores)) * 100
        print(f"  • {grupo:20s} - {count:4d} ({percentage:5.1f}%)")
    print()
    
    # ============================================================
    # 7. Query avançada: Sensores de um grupo EM um módulo
    # ============================================================
    print("[7] QUERY AVANÇADA: Sensores de GRUPO em MÓDULO específico")
    print("-" * 80)
    
    grupo_exemplo = "CH4"
    modulo_exemplo = "M05"
    
    sensores = session.query(SensorConfig).filter(
        (SensorConfig.grupo == grupo_exemplo) &
        (SensorConfig.modulo == modulo_exemplo)
    ).limit(5).all()
    
    print(f"Grup {grupo_exemplo} no Módulo {modulo_exemplo}")
    print(f"Encontrados: {len(sensores[:5])} (mostrando até 5)\n")
    
    for sensor in sensores:
        print(f"  • {sensor.sensor_id:20s} | {sensor.name[:50]:50s}")
    print()
    
    # ============================================================
    # 8. Resumo estatístico
    # ============================================================
    print("[8] RESUMO ESTATÍSTICO")
    print("-" * 80)
    
    total_sensors = repo.count()
    sensors_with_grupo = session.query(SensorConfig).filter(
        SensorConfig.grupo.isnot(None)
    ).count()
    sensors_with_modulo = session.query(SensorConfig).filter(
        SensorConfig.modulo.isnot(None)
    ).count()
    
    print(f"Total de sensores: {total_sensors:,}")
    print(f"Com Grupo: {sensors_with_grupo:,} ({(sensors_with_grupo/total_sensors)*100:.1f}%)")
    print(f"Com Módulo: {sensors_with_modulo:,} ({(sensors_with_modulo/total_sensors)*100:.1f}%)")
    print(f"Unique Grupos: {len(grupos)}")
    print(f"Unique Módulos: {len(modulos)}")
    print()
    
    # Close session
    session.close()
    
    print("="*80)
    print("[OK] Exemplos concluídos com sucesso!")
    print("="*80 + "\n")
    
    # Print available methods
    print("MÉTODOS DISPONÍVEIS NO SensorConfigRepository:")
    print("-" * 80)
    print("""
    # Filtrar sensores
    repo.get_by_grupo(grupo: str) -> List[SensorConfig]
    repo.get_by_modulo(modulo: str) -> List[SensorConfig]
    
    # Listar valores únicos
    repo.get_grupos() -> List[str]
    repo.get_modulos() -> List[str]
    
    # Contar sensores
    repo.count_by_grupo() -> Dict[str, int]          # {grupo: count}
    repo.count_by_modulo() -> Dict[str, int]         # {modulo: count}
    
    # Combinar com Session para queries avançadas
    session.query(SensorConfig).filter(
        (SensorConfig.grupo == "CH4") &
        (SensorConfig.modulo == "M05")
    ).all()
    """)
    print("="*80 + "\n")


if __name__ == '__main__':
    main()
