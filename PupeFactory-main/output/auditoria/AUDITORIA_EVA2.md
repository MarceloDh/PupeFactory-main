# Auditoría de PupeFactory contra EVA-2

> Informe histórico anterior a las correcciones. Para el estado actual y su evidencia, consultar `../../CHECKLIST_EVA2.md` y `../../MODELO_3FN.md`. Los hallazgos de SQLite, footer, stock y checkout descritos aquí ya fueron corregidos.

Fecha: 1 de octubre de 2026, America/Santiago. Revisión local: `6200326`.

## Dictamen

**La tienda cumple una parte importante de la implementación, pero todavía no cumple íntegramente la entrega.** El motor activo es SQLite, el footer no identifica al alumno y existen fallos en la gestión administrativa de stock y en solicitudes intercaladas de checkout. La aprobación de las pruebas existentes no elimina estos hallazgos.

Se ejecutaron **106 pruebas: todas aprobaron**, en SQLite temporal, con Django 5.2.17. El chequeo de Django no encontró errores y no se detectaron migraciones pendientes. La generación OpenAPI produjo 17 rutas. Su validación estricta no pudo completarse por una dependencia binaria incompatible en el entorno disponible.

No se asigna una nota total: 70 de los 100 puntos corresponden a una defensa oral individual que no se puede certificar examinando el repositorio. Tampoco es correcto asignar automáticamente cero a todos los componentes de un indicador mixto por el uso de SQLite: se distingue lo que está implementado de lo que incumple.

## Fuentes y alcance

- Fuente oficial: `Material Evaluativo/Es el grupo 1.pdf`, instrucciones y rúbrica de páginas 1-7 y Proyecto 1 de página 8. Se extrajo el documento completo y se revisaron visualmente las páginas aplicables.
- Fuentes complementarias: `ejemplos.jpg` y `ejemplos1.jpg`, fotografías de pizarra. Contienen referencias a CRUD, Django y JWT, templates, carro persistente, stock, refactorización, 3FN y 404 con `re_path`.
- README, checklist y decisiones técnicas se contrastaron con código y ejecución; sus marcas de cumplimiento no se aceptaron como prueba.
- Se revisaron configuración, rutas, modelos, migraciones, permisos, serializadores, servicios, administración, pruebas y plantillas de la tienda. Se inspeccionaron catálogo y ficha de producto en navegador local.
- Las reproducciones adicionales quedaron en `verificar_auditoria.py` y `resultados_reproducciones.json`, junto a este informe. Usan una base en memoria. El doble checkout se demuestra mediante intercalado determinista, no mediante hilos ni una prueba de bloqueo en PostgreSQL.
- No se modificó el código funcional, la configuración ni el checklist. El Python de `.venv` no inicia porque apunta a una instalación ausente. Se utilizó el Python incluido con Codex y los paquetes compatibles del entorno existente. No se certifica que el entorno original sea reproducible.

Estados: **Cumple** = implementación y evidencia suficiente para el alcance; **Parcial** = existe pero tiene una brecha; **No cumple** = requisito contradicho por evidencia; **Pendiente** = falta una comprobación externa o en el motor requerido.

## Matriz de requisitos oficiales

| Requisito | Estado | Evidencia y observación |
|---|---|---|
| Nombre Django relacionado con la temática | Cumple | Proyecto `pupefactory` y dominio de hardware. |
| Trabajo y autoría individual | Pendiente | Requiere defensa individual; el historial por sí solo no certifica autoría. |
| Base PostgreSQL o MySQL; excluir SQLite | **No cumple** | Configuración efectiva: `django.db.backends.sqlite3`; `.env.example` también propone SQLite. La pauta analítica y el checklist exigen específicamente PostgreSQL. |
| Conexión activa PostgreSQL | **No cumple en el entorno auditado** | Existe rama de configuración PostgreSQL, pero el proyecto funciona aquí con `db.sqlite3`. No se comprobó conexión, migraciones o ejecución PostgreSQL. |
| Modelos relacionados y ForeignKey | Cumple | Producto a categoría/marca; carro a ítems; orden a usuario/ítems; protección de productos vendidos. |
| Usuario a carro activo 1:1 | Cumple en estructura | `Carrito.usuario = OneToOneField`; `get_or_create` para obtener el recurso. |
| CHOICES explícito | Cumple | Roles de `CustomUser` y estados de `Orden` con `TextChoices`. |
| Comentarios en bloques en todo el código | Parcial | Vistas, servicios y serializadores principales tienen comentarios/docstrings. Los módulos de administración, por ejemplo `ordenes/admin.py`, no explican su lógica en bloques. |
| Footer con nombre completo | **No cumple** | Valor efectivo y visible: `Estudiante PupeFactory`. No es el nombre completo del alumno. |
| Footer con sección y año | Parcial | Se muestran `Sección 1` y `2026`; debe confirmarse la sección real. |
| Swagger/OpenAPI en `/api/docs/` | Cumple en pruebas | Vistas protegidas y esquema generado. Carga visual completa de Swagger y validación estricta pendientes. |
| Tokens access y refresh | Cumple | SimpleJWT; suite de autenticación aprobada. |
| Claims de rol | Cumple | Token incluye `user_id`, `username` y `role`. |
| Rol cliente y administrador | Cumple | `CLIENTE` y `ADMINISTRADOR`; permisos consultan el usuario autenticado en servidor. |
| Lectura pública de catálogo | Cumple | API productos/categorías pública, modificaciones restringidas. |
| Carro y transacciones protegidos | Cumple en API | `IsClienteRole` exige autenticación y rol cliente. |
| Inventario y estados restringidos a administración | Cumple en API | `IsAdminOrReadOnly` e `IsAdminRole`. Atención a diferencias de permisos web indicadas más abajo. |
| Carro persistente tras logout/reconexión | Cumple en SQLite; pendiente PostgreSQL | Suite y reproducción con logout real y otra sesión: conserva una unidad. |
| Evitar registros duplicados de producto en carro | Cumple en flujo normal | `UniqueConstraint(carrito, producto)` y acumulación. Escrituras simultáneas del carro no están coordinadas. |
| Agregar, modificar cantidad y eliminar | Cumple en flujo normal | API y web implementadas; 26 pruebas de carro aprobadas. |
| Agregar al carro no descuenta stock | Cumple | Servicio de carro no modifica producto; prueba específica aprobada. |
| Checkout genera orden histórica | Cumple en flujo normal | Orden e ítems se crean dentro de transacción. |
| Precios congelados al comprar | Cumple frente a cambios del catálogo | `OrdenItem.precio_unitario`; prueba de cambio posterior aprobada. No significa inmutabilidad absoluta ante edición administrativa. |
| Stock descontado al confirmar PAGADO | Parcial | Checkout crea directamente PAGADO y descuenta; transición PENDIENTE a PAGADO también descuenta. Edición directa de estado en Django Admin omite ambas reglas. |
| Rechazar pago por stock insuficiente | Cumple en servicio/API | Prueba de rechazo y rollback aprobada. Garantía bajo concurrencia PostgreSQL pendiente. |
| CANCELADO repone stock descontado | **Parcial** | Servicio/API funcionan. `OrdenAdmin.save_model` heredado guarda CANCELADO sin reposición. Reproducción: stock 8 permanece 8, debía volver a 10. |
| Estados PENDIENTE, PAGADO, ENTREGADO y CANCELADO | Parcial | Matriz legal en servicio; Django Admin permite modificar estado sin aplicarla. No existe flujo de cliente que cree una orden pendiente antes del pago. |
| Vaciar carro tras compra conservando entidad | Cumple en flujo normal | Se eliminan ítems, permanece `Carrito`. Falta bloquear el carro durante la lectura y el checkout. |
| Transacciones atómicas | Cumple en estructura; parcial en garantía | Uso real de `transaction.atomic`. Dos solicitudes que ya leyeron el mismo carro pueden convertirlo en dos órdenes. |
| Filtros con django-filter | Cumple en API | Categoría, marca, `precio_min`, `precio_max`, disponible. Suite aprobada. |
| Búsqueda de catálogo | Cumple con parámetro real | API usa `search`; interfaz web usa `q`. README anuncia incorrectamente `q` para la API. |
| Producto con nombre, marca, precio, SKU, descripción y stock | Cumple | Campos, validaciones y relaciones presentes. |
| Administrador gestiona categorías y productos | Cumple en API | ModelViewSets con permisos por rol y protección de categorías con productos. |
| Cliente explora catálogo completo | **Parcial** | 42 productos activos locales; plantilla muestra 12 sin enlaces de paginación. Página 2 existe en servidor pero no se ofrece navegación. |
| Cliente consulta detalle | Cumple | Vista y API implementadas; ficha de producto inspeccionada en navegador. |
| Cliente consulta solo sus órdenes | Cumple | Consultas restringidas a `usuario=request.user` y pruebas de aislamiento aprobadas. |
| Publicación GitHub antes del límite | Pendiente | Remoto `origin` configurado. El intento de consulta web no pudo obtener el repositorio. No se comprobó publicación del commit actual ni se conoce la hora límite. |

## Matriz de endpoints del Proyecto 1

| Operación oficial | Implementación | Resultado |
|---|---|---|
| Público GET `/api/productos/` | `ProductoViewSet` | Cumple |
| Público GET `/api/categorias/` | `CategoriaViewSet` | Cumple |
| Cliente GET/POST/DELETE `/api/carro/` | `CarritoAPIView` | Cumple en casos cubiertos |
| Cliente POST `/api/ordenes/checkout/` | `CheckoutAPIView` | Parcial por solicitudes intercaladas |
| Cliente GET `/api/mis-ordenes/` | `MisOrdenesAPIView` | Cumple |
| Administrador POST/PUT/DELETE `/api/productos/` | `ProductoViewSet` | Cumple; DELETE aplica baja lógica |
| Administrador PATCH `/api/ordenes/{id}/estado/` | `OrdenEstadoAPIView` | Cumple en casos cubiertos; revisar pago de producto inactivo |

Además existen PATCH/DELETE por producto de carro, marcas, detalle de orden, listado administrativo, registro, refresh y especificaciones. Son funcionalidades adicionales.

## Pizarra y calidad de arquitectura

| Referencia | Estado | Observación |
|---|---|---|
| Django y templates | Cumple | Plantillas heredan `base.html`; autenticación web por sesiones. JWT está implementado en la API; la pauta no obliga a usar JWT en cada formulario HTML. |
| CRUD | Cumple en API | Categorías, marcas y productos. Las órdenes usan acciones de negocio. |
| Carrito persistente | Parcial para entrega | Persistencia comprobada en SQLite; falta demostrarla en PostgreSQL. |
| Descuento de stock | Parcial | Correcto en servicio, omitido en administración directa. |
| Refactorización / Refactoring Guru | Parcial | Servicios compartidos separan lógica de negocio. Persisten `except Exception` amplios y reglas de rol web inconsistentes; no basta con declarar “Clean Architecture”. |
| 3FN | Parcial en justificación | Tablas separadas de categoría/marca y asociaciones razonables. No hay demostración formal de dependencias funcionales. El precio histórico representa el hecho de la venta; conservarlo no demuestra por sí solo toda la 3FN. El total de orden es un agregado almacenado y debe justificarse y mantenerse consistente. |
| 404 con `re_path` | Cumple | Ruta final, handler404, plantilla HTML y respuesta JSON API; tres pruebas core aprobadas. |
| Swagger reservado a administración | Cumple en pruebas | Cliente/anónimo bloqueados, administrador autorizado; protección en backend. Es un criterio adicional del checklist interno, no una exigencia explícita de las fotografías legibles. |

La foto `ejemplos1.jpg` también muestra un esquema de mall/SaaS y superadministración. No se considera un requisito de implementar múltiples tiendas en Proyecto 1: el PDF asigna una tienda de hardware con dos roles. Tampoco se exige ticket UUID: esa referencia de la rúbrica oral corresponde al proyecto de eventos y no está en la descripción del Proyecto 1.

## Hallazgos y correcciones prioritarias

### A1. Motor de entrega incorrecto — prioridad alta

Evidencia: motor efectivo SQLite y `.env.example` con `DB_ENGINE=sqlite3`. El soporte PostgreSQL en `settings.py` no demuestra conexión activa. Además, SQLite no aplica el bloqueo de filas de `select_for_update` que se invoca en el código.

Corrección: configurar PostgreSQL para la entrega, aplicar migraciones, ejecutar pruebas allí y demostrar persistencia y concurrencia con conexiones independientes. Conservar SQLite solo para tareas locales que no se presenten como evidencia de cumplimiento PostgreSQL.

### A2. Django Admin permite omitir reglas de orden — prioridad alta

Evidencia: `apps/ordenes/admin.py:6` y `:12`. Solo el precio unitario del inline es de solo lectura. Estado, total, bandera de reposición y detalles pueden alterarse mediante el formulario; no se delega en `OrdenService`.

Reproducción mediante el método usado por el guardado de Admin: compra de dos unidades sobre stock 10 deja stock 8; guardar CANCELADO mantiene stock 8. La prueba invoca `save_model` directamente, no simula el formulario completo en navegador.

Corrección: hacer inmutables los campos históricos y gestionar cambios de estado mediante acciones que usen el servicio. Impedir modificaciones de cantidad, producto y total que desajusten inventario e historial.

### A3. Dos solicitudes pueden comprar dos veces el mismo carro — prioridad alta

Evidencia: `apps/ordenes/services.py:42-50`. Se leen los ítems antes de abrir la transacción y no se bloquea la fila del carrito. Una segunda solicitud puede comprar y vaciar el carro después de esa lectura; la primera conserva los ítems antiguos y vuelve a comprar si queda stock.

Reproducción determinista: dos órdenes creadas para un solo contenido de carro, frente a una esperada. No es una demostración de hilos reales, pero reproduce el orden de operaciones permitido por el código.

Corrección: abrir transacción antes de leer, bloquear el carro y coordinar las modificaciones de sus ítems con ese bloqueo; leer contenido actualizado. Considerar idempotencia para reintentos.

### A4. Numeración y orden de bloqueo no garantizan concurrencia — prioridad media

Evidencia: `apps/ordenes/services.py:52-85`. Calcular número a partir de la última orden y consultar si existe no reserva el número. Compras de productos distintos pueden intentar el mismo número y producir un error de integridad. Este riesgo se identifica por inspección, no se reprodujo con PostgreSQL.

Ordenar la lista de IDs no ordena el bloqueo SQL. La consulta hereda `Producto.Meta.ordering = ['-id']`; se observó `ORDER BY id DESC`, mientras reposición/pago de pendientes recorren IDs ascendentes. Esa diferencia introduce riesgo de interbloqueo entre operaciones con varios productos.

Corrección: usar un identificador seguro para concurrencia, o generar el correlativo desde una secuencia/reserva atómica. Usar explícitamente un orden de filas consistente en todos los servicios y cubrirlo con pruebas PostgreSQL.

### A5. Datos reales del alumno ausentes — prioridad alta para entrega

Evidencia: settings efectivos y footer del catálogo/ficha. Nombre mostrado `Estudiante PupeFactory`; sección `Sección 1` sin validación del dato real.

Corrección: completar nombre y sección reales, y revisar footer en inicio, login, registro, catálogo, carro, checkout, historial y 404. La prueba actual comprueba que el valor configurado aparece, aunque sea un texto genérico.

### A6. Catálogo limitado a 12 sin navegación — prioridad media

Evidencia: `apps/catalogo/views.py:187`; plantilla sin `page_obj` ni enlaces `page=`. Reproducción con 14 productos: página 1 tiene 12 tarjetas y página 2 tiene 2, pero el HTML no ofrece enlace. Navegador local confirma ausencia de paginación con 42 productos activos.

Corrección: añadir navegación y conservar los filtros al cambiar de página; mostrar cantidad total y rango actual.

### A7. Pago de pendiente permite producto inactivo — prioridad media

Evidencia: `apps/ordenes/services.py:183-193` valida stock pero no `activo`. Reproducción: orden pendiente con producto desactivado pasa a PAGADO. Checkout sí rechaza producto inactivo, por lo que hay dos reglas distintas para confirmar una compra.

Corrección: unificar validaciones de disponibilidad y stock entre checkout y pago de pendientes; añadir caso de regresión.

### A8. Documentación y verificación exageran el cumplimiento — prioridad media

- README declara 96 tests; se encontraron y ejecutaron 106: usuarios 18, catálogo 35, core 3, carro 26, órdenes 24.
- README anuncia usuarios `cliente_prueba` y `admin_user`; el comando realmente genera `cliente_test` y `admin_test`. Las contraseñas dependen del entorno, no de un valor fijo garantizado.
- README documenta `q` para buscar en API; API utiliza `search`. Reproducción: `q=Audit` devuelve 14 productos y `search=Audit` devuelve 1.
- Checklist dice conexión activa y persistencia en PostgreSQL probadas: aquí el motor es SQLite.
- `apps/ordenes/tests.py:220` llama “simultáneas” a dos compras ejecutadas secuencialmente. No verifica bloqueo pesimista real.
- Las afirmaciones de imposibilidad de sobreventa/deadlocks exceden lo demostrado.

Corrección: actualizar documentos para reflejar evidencia real; agregar pruebas de concurrencia en PostgreSQL y casos de Admin y reintento de checkout.

### A9. Brechas secundarias de interfaz y autorización web

- Los filtros de precio funcionan en API; la vista web no procesa `precio_min/precio_max` ni ofrece controles. Reproducción: mínimo superior a todos los precios sigue mostrando 12 tarjetas. No es incumplimiento del filtro API obligatorio, pero limita la interfaz.
- Carro y checkout usan columnas fijas inline de `340px` y `380px`; no hay adaptación específica en el CSS examinado. Riesgo de desbordamiento móvil pendiente de medir con carro/checkout autenticados.
- La plantilla de detalle muestra descripción pero no recorre `producto.especificaciones`, aunque existen campo y endpoint. La tabla técnica prometida no está renderizada allí.
- Agregar/ver carro web admite superusuario; actualizar/eliminar/vaciar solo exige login, mientras API exige CLIENTE. Unificar la política. El aislamiento por propietario evita acceso a carros ajenos en esos métodos.
- `crear_usuarios_prueba` pone `is_staff=True` al administrador, pero no asigna permisos de modelos ni superusuario: poder entrar en Admin no garantiza gestionar sus modelos. La gestión API sí depende del rol.
- Registro API exige longitud mínima, pero no utiliza todos los validadores de contraseña que sí aplica el formulario web; uniformar validación si se mantiene el registro API.

## Evaluación de los 30 puntos técnicos

| Indicador | Máximo | Resultado de auditoría |
|---|---:|---|
| Conexión DB, CHOICES y filtros | 6 | CHOICES y filtros API cumplen; conexión PostgreSQL incumplida. No certificable como sobresaliente. |
| JWT y roles | 8 | Implementación y suite funcionales en el alcance auditado; diferencias web secundarias requieren consistencia. |
| Persistencia del carro | 8 | Persistencia real y unicidad comprobadas en SQLite; falta evidencia en PostgreSQL y coordinación de escrituras concurrentes. |
| Stock y transacciones | 8 | Flujo normal/API probado; incumplimiento al editar desde Admin y doble checkout reproducido. |

No se inventa un puntaje intermedio: algunas combinaciones encontradas no encajan literalmente en las cuatro descripciones de la pauta. El docente determina el puntaje aplicable después de corregir y demostrar.

## Preparación y límites de los 70 puntos orales

| Criterio | Puntos | Evidencia que debe explicar y demostrar el alumno |
|---|---:|---|
| Arquitectura, DB y modelos | 12 | PostgreSQL funcionando, relaciones 1:1/1:N, CHOICES, restricciones y justificación del modelo. |
| JWT, claims y RBAC | 12 | Obtención/refresh; dónde se agrega el rol; permisos consultan `request.user.role`; distinguir sesión y JWT. |
| Carro persistente | 12 | Mostrar una compra en carro, logout, otra sesión/dispositivo y conservación de ítems en PostgreSQL. |
| Checkout y stock | 12 | Explicar atomicidad, bloqueo, precio histórico, rechazo, cancelación y los arreglos de concurrencia. |
| Filtros y OpenAPI | 10 | Demostrar filtros reales, `search` y documentación con permisos correctos; validar esquema. |
| Código, comentarios y footer | 12 | Mostrar datos reales y explicar decisiones de refactorización con ejemplos del código. |

Todos estos criterios quedan **pendientes de defensa individual**, aunque existan documentación y ejemplos para prepararla.

## Evidencia de ejecución y pendientes

| Verificación | Resultado |
|---|---|
| Chequeo Django con Python alternativo compatible | Sin errores |
| Migraciones frente a modelos (`check`, `dry_run`) | Sin cambios pendientes |
| Suite existente | 106/106 aprobadas; 278,944 segundos; SQLite temporal |
| Reproducciones adicionales | Admin sin reposición, doble checkout intercalado, pago inactivo, falta paginación y diferencias de búsqueda/filtros confirmados |
| OpenAPI generado | 17 rutas, generación exitosa |
| Validación estricta OpenAPI | Pendiente: `rpds.rpds` no disponible para el Python alternativo |
| Navegador | Catálogo y ficha renderizan; footer genérico y catálogo sin navegación confirmados |
| PostgreSQL y concurrencia de conexiones reales | Pendientes |
| GitHub remoto y hora límite | Pendientes de verificación externa |
| Vista móvil completa, flujo autenticado en navegador y Swagger visual | Pendientes; flujos web principales cubiertos por suite Django |

Orden recomendado de trabajo: PostgreSQL y entorno reproducible; reglas de Admin e historial; coordinación del carro y numeración; nombre/sección; paginación y documentación; pruebas reales en PostgreSQL y ensayo de defensa.
