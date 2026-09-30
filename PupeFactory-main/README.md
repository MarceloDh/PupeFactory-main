# PupeFactory — PC Hardware Store

> **Evaluación EVA-2 — Desarrollo Backend**  
> **Carrera / Asignatura:** Desarrollo Backend  
> **Grupo 1:** PupeFactory (Tienda Especializada en Hardware y Componentes PC)  
> **Ponderación:** 25% de la Asignatura (30% Desarrollo Técnico + 70% Defensa Oral)

---

## 📋 Descripción del Proyecto

**PupeFactory** es una plataforma e-commerce de alto rendimiento especializada en la venta de componentes y hardware de computadores (CPUs, GPUs, RAM, Almacenamiento SSD/HDD, Placas Madre, Fuentes de Poder, Gabinetes y Refrigeración).

El backend está diseñado bajo principios de **Clean Architecture** y **Diseño Transaccional Seguro**:
- **Persistencia Relacional en PostgreSQL / SQLite:** Normalización en Tercera Forma Normal (3FN), integridad referencial estricta y restricciones a nivel de base de datos (`CheckConstraint`, `UniqueConstraint`).
- **Autenticación Híbrida y RBAC:** Doble esquema con **Django Sessions** para la interfaz web y **SimpleJWT** con claims personalizados de rol (`CLIENTE` y `ADMINISTRADOR`) para la API REST.
- **Carro de Compras Persistente 1:1:** Asociado al usuario en base de datos; sobrevive a cierres de sesión, reinicios de navegador y cambios de dispositivo.
- **Transacciones Atómicas y Bloqueo Pesimista:** Descuento de stock en checkout mediante `transaction.atomic()` y `select_for_update()`, garantizando la imposibilidad de sobreventas, condiciones de carrera o stock negativo.
- **Congelamiento de Precio Histórico (3FN):** Las órdenes almacenan el precio unitario inmutable al momento de la compra en `OrdenItem.precio_unitario`.
- **Máquina de Estados de Orden y Reposición de Inventario:** Control de transiciones legales (`PENDIENTE` -> `PAGADO` -> `ENTREGADO` / `CANCELADO`) con reposición atómica de stock ante cancelación y bandera anti-duplicidad `stock_reincorporado`.
- **Documentación Swagger / OpenAPI Privada:** Protegida en backend a nivel de servidor (`/api/docs/` y `/api/schema/`) exclusivamente para administradores.

---

## 🛠️ Tecnologías Utilizadas

- **Lenguaje:** Python 3.11+
- **Framework Web & API:** Django 5.x, Django REST Framework (DRF) 3.15+
- **Autenticación JWT:** `djangorestframework-simplejwt`
- **Documentación OpenAPI 3.0:** `drf-spectacular`
- **Filtros Avanzados:** `django-filter`
- **Bases de Datos:** PostgreSQL (`psycopg` / `psycopg2-binary`) y SQLite (modo local / testing)
- **Frontend Web:** Django Templates, Vanilla CSS nativo (`pupefactory.css`), SVGs inline vectoriales

---

## 🚀 Instalación y Puesta en Marcha

### 1. Clonar el Repositorio
```bash
git clone https://github.com/MarceloDh/PupeFactory-main.git
cd PupeFactory-main
```

### 2. Crear y Activar Entorno Virtual
```bash
# En Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# En Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno (`.env`)
Copiar el archivo de ejemplo `.env.example` y renombrarlo a `.env`:
```bash
cp .env.example .env
```

Configurar los parámetros requeridos en `.env`:
```ini
SECRET_KEY=clave-secreta-para-evaluacion-eva2
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Motor de Base de Datos: 'sqlite3' para pruebas locales o 'postgresql' para PostgreSQL nativo
DB_ENGINE=sqlite3
DB_NAME=pupefactory_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

# Contraseñas requeridas para el comando crear_usuarios_prueba
CLIENTE_TEST_PASSWORD=ClientePass123!
ADMIN_TEST_PASSWORD=AdminPass123!

# Datos del Estudiante (Renderizados en el footer oficial)
ALUMNO_NOMBRE=Nombre Completo Estudiante
ALUMNO_SECCION=Sección 1
ALUMNO_ANIO=2026
```

### 5. Aplicar Migraciones
```bash
python manage.py migrate
```

### 6. Crear Usuarios de Prueba (Roles RBAC)
```bash
python manage.py crear_usuarios_prueba
```
> Crea automáticamente el usuario administrador (`admin_user`) y el cliente de pruebas (`cliente_prueba`).

### 7. Poblar el Catálogo con Hardware Real
```bash
python manage.py poblar_catalogo
```
> Inserta 39 componentes de hardware reales (NVIDIA RTX 4090, Intel i9 14900K, AMD Ryzen 7 7800X3D, SSDs NVMe, RAM DDR5, etc.) con stock realista y categorización completa.

### 8. Iniciar el Servidor de Desarrollo
```bash
python manage.py runserver
```
Acceder a la aplicación web en [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

---

## 👤 Usuarios de Prueba y Credenciales

| Usuario | Contraseña por Defecto | Rol en el Sistema | Permisos y Capacidades |
| :--- | :--- | :--- | :--- |
| `cliente_prueba` | `ClientePass123!` (o la definida en `.env`) | `CLIENTE` | Comprar, gestionar carro persistente, realizar checkout, consultar historial en `/mis-ordenes/`. Bloqueado de Swagger y de modificar catálogo. |
| `admin_user` | `AdminPass123!` (o la definida en `.env`) | `ADMINISTRADOR` | Acceso a Swagger `/api/docs/`, CRUD de productos, cambio de estado de órdenes (`PATCH /api/ordenes/{id}/estado/`). Bloqueado de checkout. |

---

## 🌐 Matriz de Endpoints de la API REST

### Autenticación JWT
- `POST /api/auth/token/`: Obtención de par de tokens (`access` y `refresh`) con claims de usuario y `role`.
- `POST /api/auth/token/refresh/`: Renovación del token de acceso expirado.

### Catálogo de Productos (Público)
- `GET /api/productos/`: Listado de productos activos con filtros (`categoria`, `marca`, `precio_min`, `precio_max`, `disponible`) y búsqueda por texto (`q`).
- `GET /api/productos/{id}/`: Detalle completo del producto y disponibilidad.
- `GET /api/categorias/`: Listado maestro de categorías.
- `GET /api/marcas/`: Listado maestro de marcas.

### Carro de Compras Persistente (Rol `CLIENTE`)
- `GET /api/carro/`: Consulta del carro activo (creado de forma idempotente 1:1 si no existe).
- `POST /api/carro/`: Agrega o incrementa unidades de un producto validando stock físico.
- `PATCH /api/carro/{producto_id}/`: Actualiza directamente la cantidad deseada.
- `DELETE /api/carro/{producto_id}/`: Quita un producto del carro del usuario (Anti-IDOR).
- `DELETE /api/carro/`: Vacía todos los ítems manteniendo la entidad `Carrito`.

### Checkout y Órdenes de Compra (Rol `CLIENTE`)
- `POST /api/ordenes/checkout/`: Ejecuta compra atómica con bloqueo `select_for_update()`, descuenta stock físico, congela precios en `OrdenItem` y vacía el carro.
- `GET /api/mis-ordenes/`: Historial cronológico de compras pertenecientes exclusivamente a `request.user`.
- `GET /api/mis-ordenes/{id}/`: Detalle de una compra específica (retorna 404 ante intentos de acceso horizontal / IDOR).

### Gestión Administrativa (Rol `ADMINISTRADOR`)
- `POST /api/productos/`: Creación de nuevos productos en catálogo.
- `PUT/PATCH /api/productos/{id}/`: Edición de componentes existentes.
- `DELETE /api/productos/{id}/`: Baja lógica (`activo = False`) preservando integridad referencial en órdenes históricas.
- `PATCH /api/ordenes/{id}/estado/`: Transición de estado (`ENTREGADO` o `CANCELADO`). Al cancelar, repone stock automáticamente de forma atómica y activa `stock_reincorporado = True`.
- `GET /api/ordenes/`: Listado global de órdenes registradas en el sistema.
- `GET /api/docs/`: Interfaz interactiva Swagger UI protegida en backend.
- `GET /api/schema/`: Esquema privado OpenAPI 3.0 en formato YAML/JSON.

---

## 🧪 Verificación y Suite de Pruebas

Para garantizar la robustez del sistema y el cumplimiento de la rúbrica, ejecutar:

```bash
# 1. Comprobación del sistema sin advertencias
python manage.py check

# 2. Validación estricta del esquema OpenAPI 3.0 (código de salida 0)
python manage.py spectacular --validate

# 3. Suite completa de 96 pruebas unitarias e integrales (100% verde)
python manage.py test
```

### Distribución de los 96 Tests Automatizados:
- **`apps.usuarios` (11 tests):** Creación de `CustomUser`, claims de rol en JWT, endpoints de token y protección RBAC.
- **`apps.catalogo` (32 tests):** Filtros con `django-filter`, búsqueda multi-campo, baja lógica (soft delete), validaciones de precio positivo y stock no negativo.
- **`apps.core` (3 tests):** Renderizado de footer con datos del estudiante, respuestas 404 HTML vs 404 JSON limpio en rutas inexistentes de API.
- **`apps.carro` (26 tests):** Persistencia 1:1 en BD, validaciones de stock, prevención de duplicados, anti-IDOR y vistas web.
- **`apps.ordenes` (24 tests):** Checkout atómico, bloqueo pesimista `select_for_update()`, concurrencia sin sobreventas, congelamiento de precio histórico (3FN), transiciones de estados con reposición de inventario y vistas web de checkout/éxito/historial.

---

## 🎓 Guía para la Defensa Oral (70% de la Nota)

1. **Atomicidad con `transaction.atomic()`:**  
   Garantiza que todas las mutaciones del checkout (validación, descuento de stock en varios productos, inserción de orden e ítems históricos y vaciado de carro) se ejecuten como una única unidad lógica indivisible. Si ocurre una excepción (ej: falta de stock), se ejecuta un `ROLLBACK` total en la base de datos sin dejar datos inconsistentes.

2. **Control de Concurrencia con `select_for_update()`:**  
   En `OrdenService.checkout`, las filas de los productos comprados se bloquean a nivel de base de datos (`SELECT ... FOR UPDATE`). Si dos clientes intentan comprar simultáneamente la última unidad de una RTX 4090, el primer cliente adquiere el cerrojo, reduce el stock a 0 y confirma. El segundo cliente espera la liberación del cerrojo, lee el stock actualizado (`0`) y es rechazado con error HTTP 400 limpio sin generar sobreventas ni stock negativo.  
   Para evitar **interbloqueos (deadlocks)**, los productos se bloquean siempre ordenados por su clave primaria (`sorted([item.producto_id for item in items])`).

3. **Congelamiento de Precio Histórico y Tercera Forma Normal (3FN):**  
   `OrdenItem.precio_unitario` congela el valor del producto al momento de comprar. Esto desacopla el registro contable histórico del precio actual de catálogo en `Producto.precio`. Cumple con 3FN porque el subtotal y el total histórico no tienen una dependencia funcional transitiva respecto a las fluctuaciones futuras del catálogo.

4. **Reposición Atómica de Inventario y Control Anti-Duplicidad:**  
   Cuando una orden pasa de `PAGADO` a `CANCELADO`, `OrdenService.cambiar_estado_orden` devuelve las unidades al stock físico del producto mediante `select_for_update()` y activa `stock_reincorporado = True` dentro de la misma transacción atómica, imposibilitando que reintentos o cancelaciones repetidas dupliquen el stock.

5. **Arquitectura en Capas (`services.py` / Clean Code):**  
   Toda la lógica pesada transaccional y reglas de negocio residen en `apps/carro/services.py` y `apps/ordenes/services.py`. Las vistas (`views.py`) se mantienen delgadas, encargándose únicamente del protocolo HTTP, permisos y serialización.
