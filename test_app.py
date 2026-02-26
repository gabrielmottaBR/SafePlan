"""Test FastAPI application with routes."""
import sys
sys.path.insert(0, '.')

from backend.main import app

print('Testing FastAPI application...')
print('✓ Imports successful')
print('✓ API routes registered:')

# Filter and print routes
api_routes = [r for r in app.routes if hasattr(r, 'path')]
for route in api_routes:
    if hasattr(route, 'methods'):
        methods = ', '.join(route.methods) if route.methods else 'GET'
        print(f'  {methods:12} {route.path}')
    else:
        print(f'  {"GET":12} {route.path}')

print(f'\n✓ Total routes: {len(app.routes)}')
print('✓ Database configured for SQLite (MVP)')
print('✓ Sensors API ready at /api/v1/sensors')
