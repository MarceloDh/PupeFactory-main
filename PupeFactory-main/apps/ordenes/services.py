"""Compras y estados: carrito, orden y productos se coordinan en transacciones."""
import logging
from uuid import uuid4
from django.db import transaction
from rest_framework.exceptions import ValidationError, NotFound
from apps.carro.services import CartService
from apps.carro.models import Carrito
from apps.catalogo.models import Producto
from apps.ordenes.models import Orden, OrdenItem

logger = logging.getLogger(__name__)


class OrdenService:
    """Reglas compartidas por API, web y administración; precios históricos por ítem."""

    @staticmethod
    def _productos_bloqueados(items):
        # ORDER BY SQL determina la adquisición; ordenar el IN no basta.
        return {p.id: p for p in Producto.objects.select_for_update().filter(
            id__in=[item.producto_id for item in items]).order_by('id')}

    @staticmethod
    def _validar_compra(items, productos):
        for item in items:
            producto = productos.get(item.producto_id)
            if producto is None or not producto.activo:
                raise ValidationError({'error': 'El producto no está disponible para la venta.'})
            if producto.stock < item.cantidad:
                raise ValidationError({'error': f"Stock insuficiente para '{producto.nombre}'.", 'disponible': producto.stock})

    @classmethod
    @transaction.atomic
    def checkout(cls, user):
        # Todas las escrituras del carro usan este bloqueo antes de leer sus ítems.
        carrito = CartService.get_or_create_cart(user)
        carrito = Carrito.objects.select_for_update().get(pk=carrito.pk)
        items = list(carrito.items.order_by('producto_id'))
        if not items:
            raise ValidationError({'error': 'El carro de compras está vacío.'})
        productos = cls._productos_bloqueados(items)
        cls._validar_compra(items, productos)

        # La PK viene de una secuencia de la BD, no de una consulta MAX(id)+1.
        orden = Orden.objects.create(numero_orden=f'tmp-{uuid4().hex}', usuario=user)
        orden.numero_orden = f'#{orden.pk:04d}'
        orden.save(update_fields=['numero_orden'])
        OrdenItem.objects.bulk_create([
            OrdenItem(orden=orden, producto_id=item.producto_id, cantidad=item.cantidad,
                      precio_unitario=productos[item.producto_id].precio)
            for item in items
        ])
        orden = cls.cambiar_estado_orden(orden.pk, Orden.Estado.PAGADO, user)
        carrito.items.all().delete()
        logger.info('Checkout confirmado: %s', orden.numero_orden)
        return orden

    @classmethod
    @transaction.atomic
    def cambiar_estado_orden(cls, orden_id, nuevo_estado, user=None):
        try:
            orden_id = int(orden_id)
        except (ValueError, TypeError):
            raise ValidationError({'error': 'ID de orden inválido.'})
        orden = Orden.objects.select_for_update().filter(pk=orden_id).first()
        if orden is None:
            raise NotFound('La orden de compra no fue encontrada.')
        if nuevo_estado not in Orden.Estado.values or not orden.puede_transicionar_a(nuevo_estado):
            raise ValidationError({'error': f"Transición de estado no permitida de '{orden.estado}' a '{nuevo_estado}'."})
        items = list(orden.items.order_by('producto_id'))
        if nuevo_estado == Orden.Estado.PAGADO:
            if not items:
                raise ValidationError({'error': 'No se puede pagar una orden vacía.'})
            productos = cls._productos_bloqueados(items)
            cls._validar_compra(items, productos)
            for item in items:
                producto = productos[item.producto_id]
                producto.stock -= item.cantidad
                producto.save(update_fields=['stock', 'actualizado_en'])
        elif nuevo_estado == Orden.Estado.CANCELADO and orden.estado in (Orden.Estado.PAGADO, Orden.Estado.ENTREGADO):
            if not orden.stock_reincorporado:
                productos = cls._productos_bloqueados(items)
                for item in items:
                    producto = productos[item.producto_id]
                    producto.stock += item.cantidad
                    producto.save(update_fields=['stock', 'actualizado_en'])
                orden.stock_reincorporado = True
        orden.estado = nuevo_estado
        orden.save(update_fields=['estado', 'stock_reincorporado', 'actualizado_en'])
        return orden
