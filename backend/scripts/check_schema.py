import sys
import os

# Go to backend directory
backend_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(backend_path)
sys.path.insert(0, backend_path)

from sqlalchemy import text, create_engine

# Create engine pointing to safeplan.db
engine = create_engine('sqlite:///safeplan.db')

with engine.connect() as conn:
    result = conn.execute(text(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name='sensor_config'"
    ))
    stmt = result.scalar()
    print("CREATE TABLE Statement:")
    if stmt:
        print(stmt)
    else:
        print("Table not found!")
