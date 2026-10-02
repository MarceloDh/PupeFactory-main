"""Historial inmutable y acciones sujetas a las reglas de inventario."""
from django.contrib import admin, messages
from rest_framework.exceptions import ValidationError
from .models import Orden, OrdenItem
from .services import OrdenService


class OrdenItemInline(admin.TabularInline):
    """Productos, cantidades y precios de una venta permanecen de solo lectura."""
    model = OrdenItem
    extra = 0
    readonly_fields = ('producto', 'cantidad', 'precio_unitario', 'subtotal')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Orden)
class OrdenAdmin(admin.ModelAdmin):
    """Consulta histórica; pagar, entregar y cancelar llaman al servicio transaccional."""
    list_display = ('id', 'numero_orden', 'usuario', 'estado', 'total', 'stock_reincorporado', 'creado_en')
    list_filter = ('estado', 'stock_reincorporado', 'creado_en')
    search_fields = ('numero_orden', 'usuario__username')
    readonly_fields = ('numero_orden', 'usuario', 'estado', 'total', 'stock_reincorporado', 'creado_en', 'actualizado_en')
    inlines = [OrdenItemInline]
    actions = ['pagar', 'entregar', 'cancelar']

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        # Ningún campo editable: guardar no puede eludir la lógica del servicio.
        return

    def _transicionar(self, request, queryset, estado):
        for orden in queryset.order_by('pk'):
            try:
                OrdenService.cambiar_estado_orden(orden.pk, estado, request.user)
                self.message_user(request, f'{orden.numero_orden}: {estado}', messages.SUCCESS)
            except ValidationError as exc:
                self.message_user(request, str(exc.detail), messages.ERROR)

    @admin.action(description='Confirmar pago de órdenes pendientes')
    def pagar(self, request, queryset):
        self._transicionar(request, queryset, Orden.Estado.PAGADO)

    @admin.action(description='Marcar órdenes pagadas como entregadas')
    def entregar(self, request, queryset):
        self._transicionar(request, queryset, Orden.Estado.ENTREGADO)

    @admin.action(description='Cancelar órdenes y reponer stock pagado')
    def cancelar(self, request, queryset):
        self._transicionar(request, queryset, Orden.Estado.CANCELADO)
