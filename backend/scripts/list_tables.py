from sqlalchemy import text, create_engine, inspect

engine = create_engine('sqlite:///safeplan.db')
print(f'[*] Database: sqlite:///safeplan.db')

inspector = inspect(engine)
tables = inspector.get_table_names()
print(f'[*] Tables found: {len(tables)}')
for table in sorted(tables):
    print(f'    - {table}')

# Check if sensor_config exists
if 'sensor_config' in tables:
    print('\n[OK] sensor_config exists')
    cols = inspector.get_columns('sensor_config')
    print(f'[*] Columns: {len(cols)}')
    for col in cols[:5]:
        print(f'    - {col["name"]}')
