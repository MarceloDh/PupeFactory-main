from django.contrib import admin
from django.contrib.admin.actions import delete_selected
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from .models import Categoria, Marca, Producto, EspecificacionProducto


class EspecificacionInline(admin.TabularInline):
    """CRUD de características atómicas asociado a la ficha del producto."""
    model = EspecificacionProducto
    extra = 1


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    """CRUD de categorías; las referencias a productos impiden borrados inconsistentes."""
    list_display = ('id', 'nombre', 'slug')
    prepopulated_fields = {'slug': ('nombre',)}
    search_fields = ('nombre',)


@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    """CRUD de fabricantes, con nombre y slug únicos."""
    list_display = ('id', 'nombre', 'slug')
    prepopulated_fields = {'slug': ('nombre',)}
    search_fields = ('nombre',)


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    """Inventario editable y baja lógica para conservar referencias históricas."""
    list_display = ('id', 'nombre', 'sku', 'categoria', 'marca', 'precio', 'stock', 'activo')
    list_filter = ('categoria', 'marca', 'activo')
    search_fields = ('nombre', 'sku')
    list_editable = ('precio', 'stock', 'activo')
    inlines = [EspecificacionInline]
    actions = ['delete_selected', 'reactivar']
    delete_confirmation_template = 'admin/catalogo/producto/desactivar.html'
    delete_selected_confirmation_template = 'admin/catalogo/producto/desactivar_varios.html'

    @admin.action(description='Desactivar productos seleccionados', permissions=['delete'])
    def delete_selected(self, request, queryset):
        if not request.POST.get('post'):
            return delete_selected(self, request, queryset)
        cantidad = queryset.filter(activo=True).count()
        for producto in queryset:
            self.log_change(request, producto, 'Producto desactivado; se conserva el historial.')
        self.delete_queryset(request, queryset)
        self.message_user(request, f'{cantidad} productos desactivados. Puedes reactivarlos desde esta lista.')

    def response_delete(self, request, obj_display, obj_id):
        if request.POST.get('_popup'):
            return super().response_delete(request, obj_display, obj_id)
        self.message_user(request, f'Producto «{obj_display}» desactivado. Sus datos e historial se conservan.')
        return HttpResponseRedirect(reverse(f'{self.admin_site.name}:catalogo_producto_changelist'))

    @admin.action(description='Reactivar productos seleccionados', permissions=['change'])
    def reactivar(self, request, queryset):
        cantidad = queryset.filter(activo=False).update(activo=True, actualizado_en=timezone.now())
        self.message_user(request, f'{cantidad} productos reactivados. Conservan su stock e historial.')

    def delete_model(self, request, obj):
        obj.activo = False
        obj.save(update_fields=['activo', 'actualizado_en'])

    def delete_queryset(self, request, queryset):
        queryset.update(activo=False, actualizado_en=timezone.now())

    def get_deleted_objects(self, objs, request):
        # La confirmación describe una baja lógica: no recopilar relaciones para borrarlas.
        productos = list(objs)
        return ([str(obj) for obj in productos], {'Productos (desactivar)': len(productos)}, set(), [])
