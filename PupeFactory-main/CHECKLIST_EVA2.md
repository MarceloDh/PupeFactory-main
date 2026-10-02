# Checklist EVA-2 — Proyecto 1

Marcelo Ducommun · IEC-N4-C1 · 2026. Actualizado tras corregir la auditoría del 1 de octubre de 2026.

| Requisito técnico oficial | Estado y evidencia |
|---|---|
| Django/DRF y nombre acorde al proyecto | Implementado y ejecutado |
| PostgreSQL activo | PostgreSQL 17.11, base `pupefactory_db`; SQLite no es el motor de entrega |
| Modelos relacionados, FK y OneToOne | Modelos y migraciones aplicadas |
| CHOICES | Roles y estados de Orden |
| JWT access/refresh y claim de rol | Pruebas de autenticación aprobadas |
| Permisos públicos/cliente/administrador | API protegida, aislamiento por propietario y web de cliente consistente |
| Carro persistente tras logout | BD vinculada 1:1 y pruebas de persistencia |
| Agregar, modificar y eliminar ítems | API y web; bloqueo compartido con checkout |
| Evitar duplicados | Restricciones únicas en carro/producto y orden/producto |
| Agregar no descuenta stock | Prueba específica aprobada |
| Checkout histórico y precio congelado | OrdenItem; cambio posterior del catálogo no altera venta |
| PAGADO valida y descuenta stock | Servicio compartido por checkout, API y acciones administrativas |
| Stock insuficiente rechaza compra | Pruebas de rechazo y rollback |
| CANCELADO devuelve stock una vez | Servicio atómico; pruebas de Admin y cancelación concurrente |
| ENTREGADO y estados terminales | Transiciones explícitas y pruebas |
| Filtros django-filter | Categoría, marca, rango de precio, disponibilidad; web y API |
| Swagger/OpenAPI | Carga visual comprobada, esquema validado sin advertencias |
| Comentarios de lógica | Docstrings/bloques en modelos, servicios, permisos, vistas, serializadores y administración |
| Nombre, sección y año en footer | Marcelo Ducommun · IEC-N4-C1 · 2026; tienda, Admin y documentación |

| Referencias de pizarra y calidad | Estado |
|---|---|
| CRUD | Catálogo vía API y Django Admin; baja lógica de productos vendidos |
| 3FN | Especificaciones normalizadas y totales derivados; justificación en MODELO_3FN.md |
| Refactorización | Servicios compartidos; reglas no duplicadas en Admin |
| 404 con re_path | HTML personalizado y JSON API; pruebas aprobadas |
| Catálogo completo | Paginación visible, conserva filtros |
| Interfaz móvil de carro/checkout | Columnas adaptables y revisión visual |
| Concurrencia real | Cinco pruebas PostgreSQL con conexiones independientes |

Pendientes externos: defensa individual (70 puntos), publicación de estos cambios en GitHub y cumplimiento de la hora límite. Las instrucciones del Proyecto 1 no requieren tickets UUID ni un mall con múltiples tiendas.

Verificación final del 1 de octubre de 2026: **120 pruebas aprobadas sobre PostgreSQL**, sin errores del sistema ni migraciones pendientes. Esquema OpenAPI validado con `--fail-on-warn`. Checkout revisado a 390 px: contenido de 375 px dentro de área útil de 375 px, sin desbordamiento horizontal. Se conservan 42 productos, 265 especificaciones y 2 órdenes originales. La cuenta temporal de revisión visual fue retirada sin generar compras.
