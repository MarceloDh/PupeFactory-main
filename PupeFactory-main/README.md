# PupeFactory — Tienda de componentes PC

Proyecto 1, EVA-2 de Desarrollo Backend. **Marcelo Ducommun · IEC-N4-C1 · 2026**.

Django y Django REST Framework con PostgreSQL, JWT con roles, catálogo y CRUD administrativo, carro persistente, órdenes con precios históricos y control transaccional de stock. Es una aplicación académica: confirmar la compra simula la confirmación de pago, sin integrar una pasarela bancaria.

## Iniciar en este equipo

Desde la carpeta que contiene `manage.py`:

```powershell
.\iniciar.ps1
```

Abre la tienda en `http://127.0.0.1:8000/`. El script inicia PostgreSQL local si hace falta, aplica migraciones y usa el entorno `.venv` reparado. La base escucha únicamente en `127.0.0.1:5432`.

```powershell
.\scripts\postgresql.ps1 status
.\scripts\postgresql.ps1 stop
```

Las credenciales están en `.env`, excluido de Git. El entorno anterior está respaldado en `.venv-original`; la base SQLite original, en `.runtime/db-antes-de-correcciones.sqlite3`. Se trasladaron a PostgreSQL 42 productos, 265 atributos técnicos y 2 órdenes con sus ítems.

## Instalación en otro equipo

Requisitos: Python 3.12 o superior y PostgreSQL 17. Los binarios locales de este equipo y sus datos están excluidos de Git. Instalar PostgreSQL desde su [distribución para Windows](https://www.postgresql.org/download/windows/) o desde [EDB](https://www.enterprisedb.com/download-postgresql-binaries).

Desde el repositorio, entrar a la subcarpeta `PupeFactory-main`, donde está `manage.py`:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Editar `.env`: definir `SECRET_KEY`, `DB_PASSWORD` y las contraseñas de demostración. Mantener `DB_ENGINE=postgresql`. Crear una base y un usuario dedicados en PostgreSQL, sustituyendo la contraseña del ejemplo por la elegida:

```sql
CREATE ROLE pupefactory LOGIN CREATEDB PASSWORD 'TU_CLAVE_LOCAL';
CREATE DATABASE pupefactory_db OWNER pupefactory;
```

`CREATEDB` permite crear la base temporal de pruebas; no se otorgan permisos de superusuario a la aplicación. Los datos se generan con:

```powershell
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py crear_usuarios_prueba
.\.venv\Scripts\python.exe manage.py poblar_catalogo
.\.venv\Scripts\python.exe manage.py runserver
```

## Roles, CRUD y rutas

| Rol | Capacidades |
|---|---|
| Público | Inicio, catálogo, filtros y detalle de productos activos |
| CLIENTE | Agregar/modificar/eliminar ítems, comprar y consultar sus órdenes |
| ADMINISTRADOR | CRUD de productos/categorías/marcas, atributos técnicos, gestión de estados y documentación API |

Usuarios de demostración: **`cliente_test` y `admin_test`**. Las contraseñas son las variables `CLIENTE_TEST_PASSWORD` y `ADMIN_TEST_PASSWORD` del `.env`. El comando solo funciona con `DEBUG=True`. El administrador tiene permisos de catálogo y órdenes mediante el grupo “Gestores de tienda”; no necesita ser superusuario.

- Tienda: `/`, `/catalogo/`, `/carro/`, `/checkout/`, `/mis-ordenes/`.
- Registro/login/logout: `/accounts/register/`, `/accounts/login/`, `/accounts/logout/` (logout por POST).
- CRUD web: `/admin/`; productos vendidos se desactivan, preservando el historial.
- Swagger: `/api/docs/`; esquema: `/api/schema/`. Requieren sesión administrativa o JWT de administrador.

| Método | API | Acceso |
|---|---|---|
| POST | `/api/auth/token/`, `/api/auth/token/refresh/`, `/api/auth/register/` | Público |
| GET | `/api/productos/`, `/api/productos/{id}/`, `/api/categorias/`, `/api/marcas/` | Público |
| POST/PUT/PATCH/DELETE | Productos, categorías y marcas | Administrador |
| GET/POST/DELETE | `/api/carro/` | Cliente |
| PATCH/DELETE | `/api/carro/{producto_id}/` | Cliente |
| POST | `/api/ordenes/checkout/` | Cliente |
| GET | `/api/mis-ordenes/`, `/api/mis-ordenes/{id}/` | Cliente propietario |
| GET | `/api/ordenes/` | Administrador |
| PATCH | `/api/ordenes/{id}/estado/` | Administrador |

Filtros API: `categoria`, `marca`, `precio_min`, `precio_max`, `disponible`. Búsqueda API: **`search`**; búsqueda web: **`q`**. Ejemplo: `/api/productos/?marca=amd&precio_max=500000&search=Ryzen`.

El inicio muestra automáticamente las categorías con productos activos y su cantidad de fichas. Cada producto tiene una ficha técnica editable en Admin; el favicon de PupeFactory se comparte con la tienda, Admin y documentación. Para completar atributos ausentes sin modificar stock o precios, ejecutar `manage.py completar_fichas`. Las referencias de las cinco fichas completadas están en `FUENTES_FICHAS.md`.

## Stock, estados y 3FN

Agregar al carro no descuenta stock. Checkout bloquea el carro antes de leerlo, bloquea productos en orden de ID, crea la orden y sus precios históricos, valida el pago, descuenta inventario y vacía los ítems dentro de una transacción. Dos solicitudes al mismo carro generan una sola compra; la siguiente recibe rechazo por carro vacío.

La numeración proviene de la PK asignada por la base, evitando `MAX(id)+1`. Los números pueden contener saltos por transacciones rechazadas; no se presentan como una secuencia contable sin huecos.

Estados: PENDIENTE → PAGADO → ENTREGADO o CANCELADO; PENDIENTE también puede cancelarse. Cancelar una orden pagada repone stock una vez. Las acciones de Django Admin usan el mismo servicio y los detalles de venta son de solo lectura.

La justificación de normalización está en **MODELO_3FN.md**: categoría y marca en tablas maestras, atributos técnicos en filas propias, ítems relacionados y totales calculados desde cantidades y precios históricos. Las migraciones preservan las especificaciones anteriores.

## Verificación

### Editor Antigravity / VS Code

El repositorio tiene dos carpetas con el mismo nombre. Los archivos `pyrefly.toml` configuran la raíz de importaciones y el entorno `.venv` tanto si abres la carpeta exterior como la de `manage.py`. El análisis básico permanece activo; no se deshabilitan los diagnósticos para esconder errores.

Si el editor conserva un Python anterior, usa **Python: Select Interpreter** y elige `PupeFactory-main/.venv/Scripts/python.exe` respecto a la carpeta exterior (o `.venv/Scripts/python.exe` dentro del proyecto). Después ejecuta **Developer: Reload Window** desde la paleta de comandos para renovar los diagnósticos.

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\.venv\Scripts\python.exe manage.py spectacular --validate --fail-on-warn
.\.venv\Scripts\python.exe manage.py test --settings=pupefactory.settings_test --noinput
```

Las pruebas usan una base temporal en PostgreSQL. `settings_test` cambia únicamente el hash de contraseñas para acelerar datos de prueba; el funcionamiento habitual mantiene los hash seguros de Django. Cinco casos usan hilos y conexiones independientes para comprobar checkout compartido, última unidad, numeración, incrementos y cancelación.

El checklist diferencia implementación comprobada de defensa oral y publicación. Publicar los cambios en GitHub antes del límite y defender individualmente el proyecto son condiciones externas a ejecutar la tienda localmente.
