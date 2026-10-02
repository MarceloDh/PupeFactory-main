# Guía de defensa individual — PupeFactory

Marcelo Ducommun · IEC-N4-C1 · EVA-2, Proyecto 1.

La defensa vale 70 puntos. Practica cada explicación señalando el código y demostrando su resultado. No basta con leer nombres de librerías o decir que las pruebas aprobaron. Los tiempos siguientes son una propuesta de ensayo, no una duración exigida por la pauta.

## Preparación

1. Inicia la aplicación con `iniciar.ps1`. Usa la dirección que muestre el servidor; normalmente `http://127.0.0.1:8000/`.
2. Ten un navegador normal para el administrador y otro perfil o ventana privada para el cliente. Así conservas ambas sesiones durante la demostración.
3. Usa `admin_test` y `cliente_test`. Las contraseñas están en tu `.env`; no lo proyectes ni lo publiques.
4. Desde Admin, crea un producto de demostración con SKU propio, precio $10000 y stock 5. Usa ese producto para la compra y cancelación, evitando alterar órdenes anteriores.
5. Ten abiertos los archivos indicados abajo. Repasa `MODELO_3FN.md` y ejecuta las comprobaciones del README antes de presentar.

## Introducción — 30 segundos

«PupeFactory es una tienda de componentes de computador. El catálogo tiene lectura pública; el cliente conserva su carro y consulta sus compras; el administrador gestiona productos y estados de las órdenes. El backend utiliza Django, Django REST Framework y PostgreSQL. La API autentica con JWT y las páginas web usan sesiones de Django. Confirmar una compra simula la confirmación de pago; no hay una pasarela bancaria integrada.»

## 1. Arquitectura, base de datos y modelos — 12 puntos

**Explicación:** «Dividí el dominio en usuarios, catálogo, carro y órdenes. Las rutas dirigen la solicitud a una vista; los serializadores validan y representan los datos; los servicios concentran las reglas de compra; los modelos y PostgreSQL guardan los datos y sus restricciones. Las páginas se renderizan con templates.»

**Código:** `pupefactory/settings.py`, `pupefactory/urls.py`, `apps/catalogo/models.py`, `apps/carro/models.py`, `apps/ordenes/models.py`.

**Relaciones que debes identificar:**

- Usuario a carro: `OneToOneField`; cada usuario tiene como máximo un carro y se crea cuando lo necesita.
- Categoría y marca a productos: uno a muchos mediante `ForeignKey`.
- Carro a ítems y orden a ítems: uno a muchos. Cada ítem referencia un producto.
- Usuario a órdenes: uno a muchos; puede hacer varias compras.

**CHOICES:** muestra `Orden.Estado` y `TRANSICIONES_VALIDAS`. `TextChoices` declara los valores permitidos; la matriz y el servicio controlan qué cambio es válido. No son la misma responsabilidad.

**PostgreSQL:** señala el bloque `DATABASES`, cuyo motor de entrega es PostgreSQL. Las credenciales se leen de variables de entorno. Explica que las migraciones convierten cambios de modelos en cambios de estructura de la base. No muestres contraseñas.

**3FN:** «Categoría y marca tienen tablas propias; producto guarda sus referencias. Las características técnicas ocupan filas de EspecificacionProducto, únicas por producto y clave. En los ítems de venta, cantidad y precio pactado dependen de la combinación orden/producto. Los totales se calculan y no se guardan duplicados. No repito nombres de cliente, categoría o fabricante en los ítems.» Consulta la justificación completa en `MODELO_3FN.md`.

## 2. JWT, claims y permisos — 12 puntos

**Explicación:** «El login de la API valida las credenciales y devuelve un access token y un refresh token. El access permite autenticar solicitudes; el refresh permite obtener un nuevo access mientras siga válido. En `get_token` incorporo `user_id`, `username` y `role`. JWT está firmado; su contenido no debe confundirse con datos cifrados.»

**Código:** `apps/usuarios/serializers.py`, clase `CustomTokenObtainPairSerializer`; `apps/usuarios/permissions.py`; configuración de autenticación en `pupefactory/settings.py`.

**Autorización:** «Autenticación identifica al usuario; autorización determina qué puede hacer. Las clases de permisos consultan `request.user.role` en el servidor. El cliente no puede concederse permisos enviando un rol en el cuerpo. El registro crea clientes; no permite elegir ADMINISTRADOR.»

**Demostración con un cliente REST, por ejemplo Postman:**

1. Envía POST `/api/auth/token/` con JSON `{"username":"cliente_test","password":"TU_CLAVE_LOCAL"}`. Usa tu contraseña real únicamente en la herramienta local.
2. Muestra que devuelve `access`, `refresh` y datos de usuario. Si inspeccionas el payload, hazlo localmente; no pegues tokens vigentes en servicios externos.
3. Envía GET `/api/carro/` con `Authorization: Bearer <access>`: debe permitir el acceso al cliente.
4. Intenta POST `/api/productos/` con ese mismo token: debe rechazarlo por permisos.
5. Envía POST `/api/auth/token/refresh/` con `{"refresh":"<refresh>"}`: devuelve un nuevo access.

**Distinción importante:** el formulario web de login usa sesión/cookie y protección CSRF. Mostrar solo ese formulario no demuestra JWT. Swagger admite acceso administrativo; usar Postman con Bearer permite demostrar los roles sin mezclar la sesión de Admin.

`role=ADMINISTRADOR` es el rol del negocio; `is_staff` permite entrar en Django Admin y allí se necesitan también permisos de modelos. No son equivalentes.

## 3. Carro persistente — 12 puntos

**Explicación:** «Los ítems se guardan en PostgreSQL asociados al carro del usuario. Logout termina la sesión, pero no elimina el carro ni sus ítems. Al volver a autenticar al mismo usuario, `get_or_create(usuario=user)` recupera ese carro.»

**Código:** `apps/carro/models.py` y `CartService.get_or_create_cart` en `apps/carro/services.py`.

**Demostración:** entra como cliente, agrega dos unidades del producto de demostración, cierra sesión y vuelve a entrar. Muestra que siguen allí. También puedes entrar con la misma cuenta desde el otro perfil para comprobar reconexión.

**Duplicados:** «La restricción única carro/producto impide filas repetidas. Agregar el mismo producto aumenta su cantidad. El servicio comprueba cantidad y disponibilidad, y coordina cambios con un bloqueo del carro.»

**Detalle clave:** agregar al carro no reserva ni descuenta inventario. Aunque se valide disponibilidad al agregar, vuelve a validarse al comprar porque otro cliente pudo comprar antes.

## 4. Checkout, transacciones y stock — 12 puntos

**Explicación siguiendo `OrdenService.checkout`, en `apps/ordenes/services.py`:**

1. Abre una transacción y bloquea la fila del carro antes de leer sus ítems.
2. Rechaza el carro vacío y bloquea los productos por ID en un orden consistente.
3. Verifica productos activos y stock suficiente.
4. Crea una orden PENDIENTE y sus ítems, guardando el precio de la venta.
5. Usa el servicio compartido para pasar a PAGADO; ese paso descuenta el stock.
6. Vacía los ítems conservando el carro. La transacción confirma todo junto.

**Por qué se necesitan dos mecanismos:** «`transaction.atomic` evita guardar una compra a medias: ante un error, revierte los cambios. `select_for_update` coordina solicitudes concurrentes bloqueando las filas hasta terminar. Una transacción por sí sola no evita que dos solicitudes lean el mismo dato.»

**Demostración numérica:** el producto empieza con stock 5. Agregar dos unidades deja stock 5. Comprar deja stock 3 y crea una orden PAGADO. Desde Admin, selecciona solo esa orden y aplica la acción de cancelar: vuelve a stock 5. Intentar cancelar de nuevo se rechaza; no llega a 7. Haz estas operaciones únicamente en la aplicación local de demostración.

**Historial:** «El carro usa el precio vigente. La orden conserva `OrdenItem.precio_unitario`; cambiar el precio actual del producto no cambia lo pactado en esa venta.»

**Admin:** muestra `apps/ordenes/admin.py`. Estado y detalles históricos son de solo lectura. Las acciones pagar, entregar y cancelar llaman al mismo servicio; no hacen un guardado directo que omita inventario.

**Concurrencia:** cinco pruebas con conexiones independientes cubren dos compras del mismo carro, dos clientes por la última unidad, numeración de órdenes, incrementos de cantidad y cancelación repetida. Un mismo carro produce una sola compra. Para la última unidad, una compra resulta válida y la otra recibe rechazo.

El checkout académico crea PENDIENTE y confirma PAGADO dentro de la misma transacción: no presenta una pantalla de pago real ni deja una orden pendiente esperando una pasarela.

## 5. Filtros, búsqueda y OpenAPI — 10 puntos

**Explicación:** «`ProductoFilter` utiliza django-filter para categoría, marca, precio mínimo/máximo y disponibilidad. El backend filtra la consulta; no se limita a esconder tarjetas. La búsqueda de la API usa `search`, mientras la web usa `q`. Swagger se genera desde las vistas y serializadores mediante drf-spectacular.»

**Código:** `apps/catalogo/filters.py`, `apps/catalogo/views.py`, `apps/core/views.py`.

**Demostración:** filtra el catálogo por marca AMD y precio máximo. Luego muestra GET `/api/productos/?marca=amd&precio_max=500000&search=Ryzen`. Abre `/api/docs/` con sesión administrativa y ubica los parámetros de productos y el checkout. Cambia de página en el catálogo y muestra que se conservan los filtros.

Si cambias el parámetro `search` por `q` en la API, no estarías demostrando su búsqueda: son interfaces diferentes.

## 6. Calidad, comentarios y footer — 12 puntos

**Explicación:** «Las reglas de negocio están en servicios compartidos por API, web y acciones administrativas. Eso reduce diferencias entre caminos de compra. Los serializadores validan entradas; los permisos controlan acceso; las restricciones de base de datos protegen unicidad y valores válidos. Los comentarios explican decisiones como el bloqueo del carro y el orden de bloqueo de productos.»

**Código y demostración:** muestra un comentario de `apps/ordenes/services.py`, una acción de `apps/ordenes/admin.py` y el footer con Marcelo Ducommun · IEC-N4-C1 · 2026. Ubica `templates/base.html`, heredado por las páginas de tienda. Admin y documentación tienen sus propias plantillas con esos mismos datos.

**CRUD:** crea, consulta y modifica tu producto de demostración. Su eliminación aplica baja lógica (`activo=False`): desaparece del catálogo público y conserva referencias históricas. Explica esa decisión antes de demostrarla; no la presentes como borrado físico. Categorías y marcas referenciadas están protegidas.

## Preguntas para ensayar sin leer

| Pregunta | Idea central de la respuesta |
|---|---|
| ¿Por qué PostgreSQL? | Es el motor exigido; guarda los datos y permite los bloqueos de filas usados para coordinar compras. |
| ¿Qué diferencia hay entre FK y OneToOne? | FK permite varias filas referenciando al mismo registro; OneToOne agrega unicidad a la relación. |
| ¿Qué ocurre si falla la compra después de crear la orden? | La transacción revierte orden, ítems y cambios de stock; el carro conserva su contenido. |
| ¿Qué pasa si dos clientes compran la última unidad? | El bloqueo hace que se resuelvan sobre stock actualizado; el segundo rechaza la compra si ya no queda stock. |
| ¿Por qué el precio histórico no rompe la 3FN? | Es un hecho distinto: precio pactado de esa venta, no el precio vigente del catálogo. |
| ¿Por qué no guardar el total? | Se deriva de cantidad por precio histórico; calcularlo evita un agregado guardado que pueda desajustarse. |
| ¿Puede un cliente ver compras ajenas cambiando el ID? | La consulta de detalle exige también `usuario=request.user`; el ID por sí solo no concede acceso. |
| ¿JWT y sesión son lo mismo? | No; la API acepta Bearer JWT y las páginas web usan la sesión de Django. |
| ¿CHOICES impide cualquier transición incorrecta? | No; define valores. El servicio verifica la matriz de transiciones y las reglas de stock. |
| ¿Cancelar siempre suma stock? | Solo repone inventario que se descontó por pago. Cancelar una pendiente no suma unidades. |
| ¿El carrito reserva productos? | No. La disponibilidad se vuelve a comprobar al pagar. |
| ¿Qué significa refactorizar aquí? | Centralizar las reglas sin duplicarlas en cada interfaz y conservar el comportamiento esperado. |
| ¿Dónde están los tickets UUID mencionados en la pauta oral? | El Proyecto 1 asignado es una tienda de hardware con órdenes; la pauta mezcla referencias de eventos. Señala la descripción del Proyecto 1 y consulta al docente si aplica un criterio adicional. |

## Ensayo final

Haz un ensayo de 10–15 minutos: introducción, modelos, JWT, persistencia, compra/cancelación, filtros y calidad. Luego contesta las preguntas anteriores sin leer. Para cada afirmación intenta indicar **qué hace, dónde está y cómo lo compruebas**.

Si no recuerdas un nombre, ubica el archivo y sigue el flujo. No atribuyas funciones inexistentes: no hay pago bancario integrado, el frontend no usa JWT para cada formulario y el código no implica por sí solo 70 puntos de defensa. Explica con honestidad tu proceso y la ayuda utilizada si el docente pregunta; lo esencial es que entiendas y puedas demostrar las decisiones.
