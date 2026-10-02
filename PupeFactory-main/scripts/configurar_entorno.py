"""Configuración local de PostgreSQL. No imprime ni versiona credenciales."""
import secrets
from pathlib import Path
from dotenv import dotenv_values, set_key

root = Path(__file__).resolve().parents[1]
env = root / '.env'
env.touch(exist_ok=True)
password = secrets.token_urlsafe(32)
for key, value in {
    'DB_ENGINE': 'postgresql', 'DB_HOST': '127.0.0.1', 'DB_PORT': '5432',
    'DB_NAME': 'pupefactory_db', 'DB_USER': 'pupefactory', 'DB_PASSWORD': password,
    'ALUMNO_NOMBRE': 'Marcelo Ducommun', 'ALUMNO_SECCION': 'IEC-N4-C1', 'ALUMNO_ANIO': '2026',
}.items():
    set_key(str(env), key, value)
values = dotenv_values(env)
if not values.get('SECRET_KEY'):
    set_key(str(env), 'SECRET_KEY', secrets.token_urlsafe(48))
(root / '.runtime' / 'pg-password.txt').write_text(password, encoding='utf-8')
print('Configuración local preparada; las credenciales permanecen en .env.')
