# Decisiones técnicas — PupeFactory

- **PostgreSQL:** motor activo de entrega. Datos locales anteriores trasladados con respaldo; credenciales en `.env` y archivos locales fuera de Git.
- **Carro:** relación 1:1 con usuario y unicidad carro/producto. Todas las escrituras adquieren el mismo bloqueo del carro que utiliza checkout, antes de leer sus ítems.
- **Inventario:** bloqueos PostgreSQL en orden ascendente de PK. Pago y cancelación viven en OrdenService y se reutilizan en API, web y Admin.
- **Estados:** checkout crea PENDIENTE y confirma PAGADO dentro de una transacción. ENTREGADO/CANCELADO son terminales. Cancelar pendiente no suma stock; cancelar pagada devuelve lo comprado una sola vez.
- **Numeración:** se usa la PK de la base para generar el número visible, con un identificador temporal único dentro de la transacción; no hay MAX+1 ni reserva mediante consulta de existencia.
- **3FN:** categorías, marcas, atributos e ítems se separan en relaciones con claves candidatas. No se persisten totales derivados. El precio histórico describe un hecho de venta distinto del precio vigente. Véase MODELO_3FN.md.
- **Historial:** detalles inmutables en Admin; baja lógica de productos por API y administración. Órdenes no se borran desde Admin.
- **JWT y sesiones:** JWT para la API y sesiones Django para formularios web. Tokens incluyen rol; los permisos consultan al usuario en servidor, no confían en un rol enviado por el cliente.
- **CRUD:** categorías y marcas se borran si no tienen productos relacionados; productos se desactivan. Atributos técnicos tienen edición inline y compatibilidad de representación en la API.
- **Verificación:** pruebas de regresión e hilos en PostgreSQL. El test secuencial original fue renombrado para no presentarlo como evidencia de simultaneidad.
- **Documentación:** Swagger privado, esquema validado, parámetros reales de búsqueda y usuarios de demostración documentados. Footer con datos del alumno en vistas HTML principales, Admin y documentación.
- **Operación local:** iniciar.ps1 usa .venv y PostgreSQL local, limitado a loopback. En otro equipo se instala PostgreSQL y se prepara .env según README; .runtime no se publica.
