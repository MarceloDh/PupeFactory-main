"""Historial inmutable y acciones sujetas a las reglas de inventario."""
from django.contrib import admin, messages
from django.urls import path, reverse
from django.shortcuts import redirect
from django.utils.safestring import mark_safe
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
    list_display = ('id', 'numero_orden', 'usuario', 'estado', 'total', 'stock_reincorporado', 'acciones_rapidas', 'creado_en')
    list_filter = ('estado', 'stock_reincorporado', 'creado_en')
    search_fields = ('numero_orden', 'usuario__username')
    readonly_fields = ('numero_orden', 'usuario', 'estado', 'total', 'stock_reincorporado', 'acciones_disponibles', 'creado_en', 'actualizado_en')
    fieldsets = (
        ('Datos de la Orden', {
            'fields': ('numero_orden', 'usuario', 'estado', 'total')
        }),
        ('Gestión y Control de Estados (Transiciones Atómicas)', {
            'description': 'Acciones operativas para el administrador. Al cancelar o procesar una devolución, el inventario físico se repone automáticamente.',
            'fields': ('acciones_disponibles', 'stock_reincorporado')
        }),
        ('Auditoría y Fechas', {
            'classes': ('collapse',),
            'fields': ('creado_en', 'actualizado_en')
        }),
    )
    inlines = [OrdenItemInline]
    actions = ['pagar', 'entregar', 'cancelar']

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        # Ningún campo editable: guardar no puede eludir la lógica del servicio.
        return

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:orden_id>/accion/<str:accion>/', self.admin_site.admin_view(self.ejecutar_accion_orden), name='ordenes_orden_accion'),
        ]
        return custom_urls + urls

    def ejecutar_accion_orden(self, request, orden_id, accion):
        mapa_acciones = {
            'pagar': Orden.Estado.PAGADO,
            'entregar': Orden.Estado.ENTREGADO,
            'cancelar': Orden.Estado.CANCELADO,
        }
        if accion not in mapa_acciones:
            self.message_user(request, "Acción no reconocida.", messages.ERROR)
            return redirect('admin:ordenes_orden_change', orden_id)

        estado_destino = mapa_acciones[accion]
        try:
            orden = OrdenService.cambiar_estado_orden(orden_id, estado_destino, request.user)
            if estado_destino == Orden.Estado.CANCELADO:
                msg = f"Orden {orden.numero_orden}: Cancelada / Devolución procesada. El stock de los productos fue reincorporado al catálogo exitosamente."
            else:
                msg = f"Orden {orden.numero_orden}: Estado transicionado con éxito a {orden.get_estado_display()}."
            self.message_user(request, msg, messages.SUCCESS)
        except ValidationError as exc:
            err = exc.detail.get('error', str(exc.detail)) if isinstance(exc.detail, dict) else str(exc.detail)
            self.message_user(request, f"Error al procesar orden: {err}", messages.ERROR)
        return redirect('admin:ordenes_orden_change', orden_id)

    @admin.display(description='Acciones Rápidas')
    def acciones_rapidas(self, obj):
        if not obj or not obj.pk:
            return "-"
        botones = []
        transiciones = obj.TRANSICIONES_VALIDAS.get(obj.estado, [])
        if Orden.Estado.PAGADO in transiciones:
            url = reverse('admin:ordenes_orden_accion', args=[obj.pk, 'pagar'])
            botones.append(f'<a class="button" style="background:#28a745;color:white;padding:3px 8px;font-size:11px;" href="{url}">Pagar</a>')
        if Orden.Estado.ENTREGADO in transiciones:
            url = reverse('admin:ordenes_orden_accion', args=[obj.pk, 'entregar'])
            botones.append(f'<a class="button" style="background:#007bff;color:white;padding:3px 8px;font-size:11px;" href="{url}">Entregar</a>')
        if Orden.Estado.CANCELADO in transiciones:
            url = reverse('admin:ordenes_orden_accion', args=[obj.pk, 'cancelar'])
            lbl = "Devolver" if obj.estado == Orden.Estado.ENTREGADO else "Cancelar"
            botones.append(f'<a class="button" style="background:#dc3545;color:white;padding:3px 8px;font-size:11px;" href="{url}" onclick="return confirm(\'¿Confirmas cancelar/devolver la orden #{obj.pk:04d}? El stock se devolverá al catálogo.\');">{lbl}</a>')
        if not botones:
            return mark_safe('<span style="color:#6c757d;font-size:11px;">Finalizada</span>')
        return mark_safe(" ".join(botones))

    @admin.display(description='Botones de Acción Disponibles')
    def acciones_disponibles(self, obj):
        if not obj or not obj.pk:
            return "-"
        botones = []
        transiciones = obj.TRANSICIONES_VALIDAS.get(obj.estado, [])
        if Orden.Estado.PAGADO in transiciones:
            url = reverse('admin:ordenes_orden_accion', args=[obj.pk, 'pagar'])
            botones.append(f'<a class="button" style="background:#28a745;color:#fff;padding:8px 14px;margin-right:10px;text-decoration:none;border-radius:4px;font-weight:bold;" href="{url}">💳 Confirmar Pago</a>')
        if Orden.Estado.ENTREGADO in transiciones:
            url = reverse('admin:ordenes_orden_accion', args=[obj.pk, 'entregar'])
            botones.append(f'<a class="button" style="background:#007bff;color:#fff;padding:8px 14px;margin-right:10px;text-decoration:none;border-radius:4px;font-weight:bold;" href="{url}">🚚 Marcar como Entregado</a>')
        if Orden.Estado.CANCELADO in transiciones:
            url = reverse('admin:ordenes_orden_accion', args=[obj.pk, 'cancelar'])
            if obj.estado == Orden.Estado.ENTREGADO:
                lbl = "🔄 Procesar Devolución (Reponer Stock al Catálogo)"
            else:
                lbl = "❌ Cancelar Compra (Reponer Stock al Catálogo)"
            botones.append(f'<a class="button" style="background:#dc3545;color:#fff;padding:8px 14px;margin-right:10px;text-decoration:none;border-radius:4px;font-weight:bold;" href="{url}" onclick="return confirm(\'¿Estás seguro de cancelar/devolver esta orden? El stock físico se reincorporará automáticamente al catálogo.\');">{lbl}</a>')
        if not botones:
            return mark_safe('<span style="color:#6c757d;font-weight:bold;font-size:13px;">🔒 No hay transiciones disponibles para esta orden (Estado terminal definitivo).</span>')
        return mark_safe(" ".join(botones))

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

    @admin.action(description='Cancelar o procesar devolución de órdenes (repone stock)')
    def cancelar(self, request, queryset):
        self._transicionar(request, queryset, Orden.Estado.CANCELADO)
