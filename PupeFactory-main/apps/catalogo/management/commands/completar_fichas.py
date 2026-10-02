"""Completa atributos ausentes sin volver a sembrar precios, stock ni productos."""
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.catalogo.models import Producto, EspecificacionProducto
from .specs_data import HARDWARE_SPECS


class Command(BaseCommand):
    help = 'Completa fichas técnicas desde los datos del catálogo, conservando los valores existentes.'

    @transaction.atomic
    def handle(self, *args, **options):
        creados = 0
        for producto in Producto.objects.order_by('pk'):
            for clave, valor in HARDWARE_SPECS.get(producto.sku, {}).items():
                _, creado = EspecificacionProducto.objects.get_or_create(
                    producto=producto, clave=clave, defaults={'valor': str(valor)})
                creados += int(creado)
        pendientes = Producto.objects.filter(activo=True, fichas_tecnicas__isnull=True).count()
        self.stdout.write(self.style.SUCCESS(f'Agregados {creados} atributos. Productos activos sin ficha: {pendientes}.'))
