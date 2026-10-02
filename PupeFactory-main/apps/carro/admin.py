from django.contrib import admin
from .models import Carrito, CarritoItem


class CarritoItemInline(admin.TabularInline):
    """Consulta del carro; las escrituras pasan por el servicio que coordina checkout."""
    model = CarritoItem
    extra = 0
    readonly_fields = ('producto', 'cantidad', 'agregado_en')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Carrito)
class CarritoAdmin(admin.ModelAdmin):
    """Carros persistentes de solo lectura, sin alterar compras desde Admin."""
    list_display = ('id', 'usuario', 'creado_en', 'actualizado_en', 'total_items', 'total')
    inlines = [CarritoItemInline]
    readonly_fields = ('usuario', 'creado_en', 'actualizado_en', 'total_items', 'total')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
