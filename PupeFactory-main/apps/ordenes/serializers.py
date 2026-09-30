from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from apps.ordenes.models import Orden, OrdenItem


class OrdenItemSerializer(serializers.ModelSerializer):
    """
    Serializador para el detalle histórico de productos comprados en una orden.
    Muestra el precio unitario CONGELADO al momento de la transacción.
    """
    producto_id = serializers.IntegerField(source='producto.id', read_only=True)
    nombre = serializers.CharField(source='producto.nombre', read_only=True)
    sku = serializers.CharField(source='producto.sku', read_only=True)
    imagen = serializers.SerializerMethodField()
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    precio_unitario = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = OrdenItem
        fields = [
            'id',
            'producto_id',
            'nombre',
            'sku',
            'imagen',
            'precio_unitario',
            'cantidad',
            'subtotal',
        ]
        read_only_fields = fields

    @extend_schema_field(serializers.CharField(allow_null=True))
    def get_imagen(self, obj):
        if obj.producto:
            return obj.producto.imagen_final
        return None


class OrdenSerializer(serializers.ModelSerializer):
    """
    Serializador completo para órdenes de compra históricas.
    Incluye datos del comprador, estado actual, total monetario, fecha y los ítems asociados.
    """
    items = OrdenItemSerializer(many=True, read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    total_items = serializers.SerializerMethodField()
    usuario = serializers.IntegerField(source='usuario.id', read_only=True)
    usuario_username = serializers.CharField(source='usuario.username', read_only=True)
    fecha = serializers.DateTimeField(source='creado_en', read_only=True)

    class Meta:
        model = Orden
        fields = [
            'id',
            'numero_orden',
            'usuario',
            'usuario_username',
            'estado',
            'estado_display',
            'total',
            'total_items',
            'stock_reincorporado',
            'fecha',
            'creado_en',
            'actualizado_en',
            'items',
        ]
        read_only_fields = fields

    @extend_schema_field(serializers.IntegerField())
    def get_total_items(self, obj):
        return sum(item.cantidad for item in obj.items.all())


class CambiarEstadoOrdenSerializer(serializers.Serializer):
    """
    Serializador para el cambio administrativo de estado de una orden.
    Solo admite transiciones válidas según las reglas del negocio (ENTREGADO o CANCELADO).
    """
    estado = serializers.ChoiceField(
        choices=Orden.Estado.choices,
        help_text="Nuevo estado para la orden (ej: ENTREGADO, CANCELADO)"
    )
