import os
from django.db import models, transaction
from django.core.validators import MinValueValidator
from decimal import Decimal


class Categoria(models.Model):
    """
    Categoría para clasificación de componentes (ej: Procesadores, Tarjetas de Video, RAM).
    Normalizada para cumplir 3FN.
    """
    nombre = models.CharField(max_length=100, unique=True, verbose_name='Nombre de la Categoría')
    slug = models.SlugField(max_length=120, unique=True, verbose_name='Slug Identificador')
    descripcion = models.TextField(blank=True, default='', verbose_name='Descripción')

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Marca(models.Model):
    """
    Marca o fabricante de los componentes (ej: ASUS, MSI, AMD, NVIDIA, Corsair).
    Normalizada para cumplir 3FN.
    """
    nombre = models.CharField(max_length=100, unique=True, verbose_name='Nombre de la Marca')
    slug = models.SlugField(max_length=120, unique=True, verbose_name='Slug Identificador')

    class Meta:
        verbose_name = 'Marca'
        verbose_name_plural = 'Marcas'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    """
    Producto o componente de hardware a la venta en PupeFactory.
    Cumple con 3FN: no contiene redundancias transitivas.
    """
    nombre = models.CharField(max_length=200, verbose_name='Nombre del Producto')
    sku = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Código SKU Único',
        help_text='Identificador único de inventario del producto'
    )
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name='productos',
        verbose_name='Categoría'
    )
    marca = models.ForeignKey(
        Marca,
        on_delete=models.PROTECT,
        related_name='productos',
        verbose_name='Marca'
    )
    descripcion = models.TextField(blank=True, default='', verbose_name='Descripción Detallada')
    precio = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Precio Actual (CLP)'
    )
    stock = models.PositiveIntegerField(
        default=0,
        verbose_name='Stock Físico Disponible'
    )
    imagen = models.ImageField(
        upload_to='productos/',
        blank=True,
        null=True,
        verbose_name='Imagen del Producto'
    )
    imagen_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='URL de Imagen Externa',
        help_text='Enlace HTTP/HTTPS a imagen del producto si no se sube archivo local.'
    )
    activo = models.BooleanField(
        default=True,
        verbose_name='¿Activo para la venta?',
        help_text='Si se desactiva, no se muestra en el catálogo público pero mantiene integridad histórica en órdenes.'
    )
    creado_en = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    actualizado_en = models.DateTimeField(auto_now=True, verbose_name='Última Actualización')

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['-id']
        constraints = [
            models.CheckConstraint(
                condition=models.Q(precio__gt=0),
                name='chk_producto_precio_positivo'
            ),
            models.CheckConstraint(
                condition=models.Q(stock__gte=0),
                name='chk_producto_stock_no_negativo'
            ),
        ]

    def __str__(self):
        return f"{self.nombre} (SKU: {self.sku}) - ${self.precio:,.0f}"

    @property
    def tiene_stock(self):
        return self.stock > 0

    @property
    def especificaciones(self):
        """Compatibilidad API: diccionario construido desde filas atómicas normalizadas."""
        if hasattr(self, '_especificaciones_pendientes'):
            return self._especificaciones_pendientes
        if not self.pk:
            return {}
        return {item.clave: item.valor for item in self.fichas_tecnicas.all()}

    @especificaciones.setter
    def especificaciones(self, value):
        self._especificaciones_pendientes = dict(value or {})

    def save(self, *args, **kwargs):
        # El CRUD conserva su representación JSON, pero persiste atributos en otra tabla.
        if not hasattr(self, '_especificaciones_pendientes'):
            return super().save(*args, **kwargs)
        with transaction.atomic():
            super().save(*args, **kwargs)
            self.fichas_tecnicas.all().delete()
            EspecificacionProducto.objects.bulk_create([
                EspecificacionProducto(producto=self, clave=clave, valor=str(valor))
                for clave, valor in self._especificaciones_pendientes.items()
            ])
            del self._especificaciones_pendientes
            if hasattr(self, '_prefetched_objects_cache'):
                self._prefetched_objects_cache.pop('fichas_tecnicas', None)

    @property
    def get_especificaciones_items(self):
        """Retorna lista de diccionarios [{'clave': k, 'valor': v}] para renderizado en tabla HTML."""
        if not self.especificaciones or not isinstance(self.especificaciones, dict):
            return []
        return [{'clave': k, 'valor': v} for k, v in self.especificaciones.items()]

    @property
    def get_imagen_url(self):
        """Retorna la URL local si el archivo físico existe en disco, la URL remota externa o no-image.svg."""
        if self.imagen:
            try:
                if hasattr(self.imagen, 'path') and os.path.exists(self.imagen.path):
                    return self.imagen.url
            except Exception:
                pass
        if self.imagen_url:
            return self.imagen_url
        return '/static/images/no-image.svg'

    @property
    def imagen_final(self):
        """Alias para get_imagen_url asegurando compatibilidad con plantillas y serializadores."""
        return self.get_imagen_url


class EspecificacionProducto(models.Model):
    """Un valor por atributo del producto: clave candidata (producto, clave), en 3FN."""
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='fichas_tecnicas')
    clave = models.CharField(max_length=100)
    valor = models.TextField()

    class Meta:
        ordering = ['id']
        constraints = [models.UniqueConstraint(fields=['producto', 'clave'], name='unique_producto_especificacion')]

    def __str__(self):
        return f'{self.clave}: {self.valor}'


