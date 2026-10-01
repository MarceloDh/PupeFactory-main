import logging
from decimal import Decimal
from django.db import transaction
from rest_framework.exceptions import ValidationError as DRFValidationError, NotFound

from apps.carro.services import CartService
from apps.catalogo.models import Producto
from apps.ordenes.models import Orden, OrdenItem

logger = logging.getLogger(__name__)


class OrdenService:
    """
    Capa de servicio de negocio para el módulo de Órdenes y Checkout.
    Centraliza las transacciones atómicas, bloqueos de concurrencia pesimistas
    (select_for_update), congelamiento de precio histórico (3FN) y reposición de inventario.
    """

    @classmethod
    def checkout(cls, user):
        """
        Ejecuta el proceso completo de compra (checkout) de forma atómica y consistente.

        Proceso:
        1. Obtiene el carrito activo persistente del usuario cliente.
        2. Valida que el carrito no esté vacío.
        3. Bloquea pesimistamente en base de datos los productos con select_for_update()
           ordenados por ID para evitar interbloqueos (deadlocks) ante compras concurrentes.
        4. Valida disponibilidad (activo=True) y stock suficiente (stock >= cantidad).
        5. Genera un número correlativo único de orden (#0001, #0002, etc.).
        6. Crea la Orden con estado PAGADO y total calculado estrictamente en Decimal.
        7. Copia cada CarritoItem como OrdenItem CONGELANDO el precio_unitario actual del producto.
        8. Descuenta atómicamente el stock físico del inventario.
        9. Vacía los ítems del carro del usuario manteniendo la instancia persistente del Carrito.
        10. Retorna la instancia de Orden creada.
        """
        if not user or not user.is_authenticated:
            raise DRFValidationError({"error": "Usuario no autenticado.", "status": 401})

        # 1. Obtener carrito activo del usuario
        carrito = CartService.get_or_create_cart(user)
        items = list(carrito.items.select_related('producto').all())

        # 2. Validar que tenga productos
        if not items:
            raise DRFValidationError({"error": "El carro de compras está vacío.", "status": 400})

        # 3. Transacción atómica con bloqueo pesimista
        with transaction.atomic():
            # Ordenar IDs de productos para prevenir deadlocks en transacciones concurrentes
            product_ids = sorted([item.producto_id for item in items])
            productos_locked = {
                p.id: p for p in Producto.objects.select_for_update().filter(id__in=product_ids)
            }

            # 4. Validar existencia, estado activo y stock de cada producto bloqueado
            for item in items:
                p = productos_locked.get(item.producto_id)
                if not p:
                    raise DRFValidationError({
                        "error": f"El producto con ID {item.producto_id} ya no existe en el catálogo.",
                        "status": 400
                    })

                if not p.activo:
                    raise DRFValidationError({
                        "error": f"El producto '{p.nombre}' no está disponible para la venta.",
                        "status": 400
                    })

                if p.stock < item.cantidad:
                    raise DRFValidationError({
                        "error": f"Stock insuficiente para '{p.nombre}'. Unidades disponibles: {p.stock}, solicitadas: {item.cantidad}.",
                        "disponible": p.stock,
                        "status": 400
                    })

            # 5. Generar número de orden único secuencial (#0001, #0002, etc.)
            last_orden = Orden.objects.order_by('-id').first()
            next_num = (last_orden.id + 1) if last_orden else 1
            numero_orden = f"#{next_num:04d}"
            while Orden.objects.filter(numero_orden=numero_orden).exists():
                next_num += 1
                numero_orden = f"#{next_num:04d}"

            # 6. Calcular total con Decimal
            total_orden = Decimal('0.00')
            for item in items:
                prod = productos_locked[item.producto_id]
                total_orden += prod.precio * item.cantidad

            # 7. Crear la orden de compra en estado PAGADO
            orden = Orden.objects.create(
                numero_orden=numero_orden,
                usuario=user,
                estado=Orden.Estado.PAGADO,
                total=total_orden,
                stock_reincorporado=False
            )

            # 8. Crear OrdenItems con PRECIO HISTÓRICO CONGELADO y descontar stock
            for item in items:
                prod = productos_locked[item.producto_id]

                OrdenItem.objects.create(
                    orden=orden,
                    producto=prod,
                    cantidad=item.cantidad,
                    precio_unitario=prod.precio  # Congelamiento inmutable de precio
                )

                # Descuento atómico de stock
                prod.stock -= item.cantidad
                prod.save(update_fields=['stock', 'actualizado_en'])

            # 9. Vaciar el carro de compras después de compra exitosa
            carrito.items.all().delete()

            logger.info(
                f"Checkout exitoso: Orden {orden.numero_orden} creada para usuario {user.username} con total ${orden.total}."
            )
            return orden

    @classmethod
    def cambiar_estado_orden(cls, orden_id, nuevo_estado, user=None):
        """
        Cambia el estado de una orden aplicando las reglas de transición de negocio
        y reposición atómica de stock si pasa a CANCELADO.

        Flujo permitido:
        PENDIENTE -> PAGADO, CANCELADO
        PAGADO -> ENTREGADO, CANCELADO
        ENTREGADO -> (terminal)
        CANCELADO -> (terminal)

        Reposición de stock:
        - Si pasa de PAGADO -> CANCELADO y stock_reincorporado es False:
          Se devuelven las unidades de cada ítem al stock físico del Producto
          y se marca stock_reincorporado = True.
        - Si ya fue reincorporado previamente: no se vuelve a sumar stock (anti-duplicidad).
        """
        with transaction.atomic():
            try:
                orden_id = int(orden_id)
            except (ValueError, TypeError):
                raise DRFValidationError({"error": "ID de orden inválido.", "status": 400})

            orden = Orden.objects.select_for_update().filter(id=orden_id).first()
            if not orden:
                raise NotFound({"error": "La orden de compra no fue encontrada.", "status": 404})

            # Validar que nuevo_estado pertenezca a los choices
            if nuevo_estado not in Orden.Estado.values:
                raise DRFValidationError({
                    "error": f"Estado '{nuevo_estado}' no es válido. Estados disponibles: {list(Orden.Estado.values)}",
                    "status": 400
                })

            # Validar si la transición es permitida
            if not orden.puede_transicionar_a(nuevo_estado):
                raise DRFValidationError({
                    "error": f"Transición de estado no permitida de '{orden.estado}' a '{nuevo_estado}'.",
                    "status": 400
                })

            estado_anterior = orden.estado

            # LÓGICA DE CANCELACIÓN Y REPOSICIÓN DE STOCK
            if nuevo_estado == Orden.Estado.CANCELADO:
                if estado_anterior == Orden.Estado.PAGADO and not orden.stock_reincorporado:
                    # Devolver productos al inventario atómicamente
                    items = orden.items.select_related('producto').order_by('producto_id')
                    for item in items:
                        producto_locked = Producto.objects.select_for_update().get(id=item.producto_id)
                        producto_locked.stock += item.cantidad
                        producto_locked.save(update_fields=['stock', 'actualizado_en'])

                    orden.stock_reincorporado = True
                    logger.info(f"Stock reincorporado al cancelar orden {orden.numero_orden}.")

            # Si pasa de PENDIENTE a PAGADO (descuenta stock si no se había descontado)
            elif nuevo_estado == Orden.Estado.PAGADO and estado_anterior == Orden.Estado.PENDIENTE:
                items = orden.items.select_related('producto').order_by('producto_id')
                for item in items:
                    producto_locked = Producto.objects.select_for_update().get(id=item.producto_id)
                    if producto_locked.stock < item.cantidad:
                        raise DRFValidationError({
                            "error": f"No se puede pasar a PAGADO. Stock insuficiente para '{producto_locked.nombre}'. Disponible: {producto_locked.stock}, requerido: {item.cantidad}.",
                            "status": 400
                        })
                    producto_locked.stock -= item.cantidad
                    producto_locked.save(update_fields=['stock', 'actualizado_en'])

            # Actualizar estado de la orden
            orden.estado = nuevo_estado
            orden.save(update_fields=['estado', 'stock_reincorporado', 'actualizado_en'])

            logger.info(f"Orden {orden.numero_orden} transicionó de {estado_anterior} a {nuevo_estado}.")
            return orden
