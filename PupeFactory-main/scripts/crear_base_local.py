"""Crea una base dedicada sin permisos globales de superusuario para la aplicación."""
import os
from pathlib import Path
import psycopg
from psycopg import sql
from dotenv import load_dotenv

root = Path(__file__).resolve().parents[1]
load_dotenv(root / '.env')
password = (root / '.runtime' / 'pg-password.txt').read_text(encoding='utf-8')
with psycopg.connect(host='127.0.0.1', port=5432, user='postgres', password=password,
                     dbname='postgres', autocommit=True) as conn:
    user = os.environ['DB_USER']
    name = os.environ['DB_NAME']
    if not conn.execute('SELECT 1 FROM pg_roles WHERE rolname=%s', (user,)).fetchone():
        conn.execute(sql.SQL('CREATE ROLE {} LOGIN CREATEDB PASSWORD {}').format(
            sql.Identifier(user), sql.Literal(os.environ['DB_PASSWORD'])))
    if not conn.execute('SELECT 1 FROM pg_database WHERE datname=%s', (name,)).fetchone():
        conn.execute(sql.SQL('CREATE DATABASE {} OWNER {}').format(sql.Identifier(name), sql.Identifier(user)))
print('Base dedicada creada. El usuario de la aplicación puede crear bases de pruebas y no es superusuario.')
