from rest_framework import serializers
from decimal import Decimal
from apps.catalogo.models import Categoria, Marca, Producto

# ==============================================================================
# SERIALIZADORES DEL CATÁLOGO DE PRODUCTOS (PupeFactory)
# ==============================================================================

class CategoriaSerializer(serializers.ModelSerializer):
    """
    Serializador para Categorías (ej: Procesadores, Tarjetas de Video, RAM).
    """
    class Meta:
        model = Categoria
        fields = ['id', 'nombre', 'slug', 'descripcion']


class MarcaSerializer(serializers.ModelSerializer):
    """
    Serializador para Marcas (ej: ASUS, MSI, AMD, NVIDIA).
    """
    class Meta:
        model = Marca
        fields = ['id', 'nombre', 'slug']


class ProductoSerializer(serializers.ModelSerializer):
    """
    Serializador para Productos de Hardware.
    Permite lectura detallada (incluye nombres de categoría y marca, y estado de stock)
    y escritura validada para operaciones CRUD administrativas.
    """
    categoria_nombre = serializers.ReadOnlyField(source='categoria.nombre')
    marca_nombre = serializers.ReadOnlyField(source='marca.nombre')
    disponible = serializers.BooleanField(source='tiene_stock', read_only=True)
    imagen_final = serializers.CharField(source='get_imagen_url', read_only=True, allow_null=True)
    especificaciones = serializers.DictField(child=serializers.CharField(), required=False)

    class Meta:
        model = Producto
        fields = [
            'id',
            'nombre',
            'sku',
            'categoria',
            'categoria_nombre',
            'marca',
            'marca_nombre',
            'descripcion',
            'especificaciones',
            'precio',
            'stock',
            'activo',
            'imagen',
            'imagen_url',
            'imagen_final',
            'disponible',
            'creado_en',
            'actualizado_en',
        ]
        read_only_fields = ['id', 'creado_en', 'actualizado_en', 'disponible', 'imagen_final']

    def validate_precio(self, value):
        """Valida que el precio sea estrictamente positivo."""
        if value <= Decimal('0.00'):
            raise serializers.ValidationError("El precio debe ser mayor a cero.")
        return value

    def validate_especificaciones(self, value):
        if any(not clave.strip() or len(clave) > 100 for clave in value):
            raise serializers.ValidationError('Cada característica debe tener un nombre de 1 a 100 caracteres.')
        return value

    def create(self, validated_data):
        """La propiedad del modelo convierte el diccionario en atributos relacionados."""
        return Producto.objects.create(**validated_data)

    def validate_stock(self, value):
        """Valida que el stock no sea negativo."""
        if value < 0:
            raise serializers.ValidationError("El stock no puede ser negativo.")
        return value

    def validate_sku(self, value):
        """Valida que el SKU sea único en el catálogo."""
        sku_clean = value.strip().upper()
        qs = Producto.objects.filter(sku__iexact=sku_clean)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Ya existe un producto registrado con este código SKU.")
        return sku_clean


class ProductoEspecificacionItemSerializer(serializers.Serializer):
    clave = serializers.CharField(help_text="Nombre de la característica técnica (ej: Socket, Frecuencia, VRAM)")
    valor = serializers.CharField(help_text="Valor o especificación técnica correspondiente")


class ProductoEspecificacionesDetailSerializer(serializers.Serializer):
    """
    Serializador para el endpoint de tabla de especificaciones técnicas:
    GET /api/productos/{id}/especificaciones/
    """
    producto_id = serializers.IntegerField()
    nombre = serializers.CharField()
    sku = serializers.CharField()
    categoria = serializers.CharField()
    marca = serializers.CharField()
    precio = serializers.DecimalField(max_digits=12, decimal_places=2)
    disponible = serializers.BooleanField()
    especificaciones = serializers.DictField(child=serializers.CharField())
    tabla = ProductoEspecificacionItemSerializer(many=True)

