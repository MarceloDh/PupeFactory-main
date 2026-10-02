"""Casos de auditoría y concurrencia real, con conexiones independientes en PostgreSQL."""
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from decimal import Decimal
from django.db import close_old_connections, connection
from django.test import TestCase, TransactionTestCase, skipUnlessDBFeature
from django.urls import reverse
from rest_framework.exceptions import ValidationError
from apps.usuarios.models import CustomUser
from apps.catalogo.models import Categoria, Marca, Producto
from apps.carro.services import CartService
from apps.ordenes.models import Orden, OrdenItem
from apps.ordenes.services import OrdenService


class DatosCompra:
    def preparar(self):
        categoria = Categoria.objects.create(nombre='CPU', slug='cpu')
        marca = Marca.objects.create(nombre='AMD', slug='amd')
        self.producto = Producto.objects.create(nombre='CPU', sku='CPU-1', categoria=categoria, marca=marca, precio=100, stock=10)
        self.cliente = CustomUser.objects.create_user(username='comprador', password='Password123!')


class RegresionesOrdenTest(DatosCompra, TestCase):
    def setUp(self):
        self.preparar()

    def test_admin_cancela_mediante_accion_y_repone_stock(self):
        administrador = CustomUser.objects.create_superuser(username='gestor', password='Password123!', role='ADMINISTRADOR')
        CartService.add_item(self.cliente, self.producto.pk, 2)
        orden = OrdenService.checkout(self.cliente)
        self.client.force_login(administrador)
        response = self.client.post(reverse('admin:ordenes_orden_changelist'), {
            'action': 'cancelar', '_selected_action': [str(orden.pk)], 'index': '0'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.producto.refresh_from_db()
        orden.refresh_from_db()
        self.assertEqual(self.producto.stock, 10)
        self.assertEqual(orden.estado, 'CANCELADO')
        self.assertTrue(orden.stock_reincorporado)

    def test_formulario_admin_no_modifica_estado_ni_historial(self):
        administrador = CustomUser.objects.create_superuser(username='gestor', password='Password123!', role='ADMINISTRADOR')
        CartService.add_item(self.cliente, self.producto.pk)
        orden = OrdenService.checkout(self.cliente)
        self.client.force_login(administrador)
        response = self.client.get(reverse('admin:ordenes_orden_change', args=[orden.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('estado', response.context['adminform'].form.fields)
        self.assertNotIn('total', response.context['adminform'].form.fields)

    def test_pendiente_inactiva_rechaza_pago_sin_mutar_stock(self):
        orden = Orden.objects.create(numero_orden='PENDIENTE-1', usuario=self.cliente)
        OrdenItem.objects.create(orden=orden, producto=self.producto, cantidad=1, precio_unitario=100)
        self.producto.activo = False
        self.producto.save()
        with self.assertRaises(ValidationError):
            OrdenService.cambiar_estado_orden(orden.pk, 'PAGADO')
        self.producto.refresh_from_db()
        orden.refresh_from_db()
        self.assertEqual(orden.estado, 'PENDIENTE')
        self.assertEqual(self.producto.stock, 10)

    def test_total_derivado_de_precio_historico(self):
        CartService.add_item(self.cliente, self.producto.pk, 2)
        orden = OrdenService.checkout(self.cliente)
        self.producto.precio = 999
        self.producto.save()
        self.assertEqual(orden.total, Decimal('200.00'))
        self.assertNotIn('total', [field.name for field in Orden._meta.fields])


@skipUnlessDBFeature('has_select_for_update')
class ConcurrenciaPostgresTest(DatosCompra, TransactionTestCase):
    """No se ejecuta como si fuera una prueba de bloqueo cuando el motor es SQLite."""
    def setUp(self):
        self.preparar()

    def ejecutar_dos(self, operaciones):
        barrera = Barrier(2)
        def ejecutar(operacion):
            close_old_connections()
            try:
                # Un bloqueo defectuoso falla con timeout, en lugar de colgar la suite.
                with connection.cursor() as cursor:
                    cursor.execute("SET lock_timeout = '5s'")
                barrera.wait(timeout=5)
                try:
                    return ('ok', operacion())
                except ValidationError:
                    return ('rechazo', None)
            finally:
                connection.close()
        with ThreadPoolExecutor(max_workers=2) as executor:
            futuros = [executor.submit(ejecutar, op) for op in operaciones]
            return [f.result(timeout=15) for f in futuros]

    def test_dos_checkout_mismo_carro_generan_una_orden(self):
        CartService.add_item(self.cliente, self.producto.pk)
        resultados = self.ejecutar_dos([lambda: OrdenService.checkout(self.cliente)] * 2)
        self.assertCountEqual([r[0] for r in resultados], ['ok', 'rechazo'])
        self.assertEqual(Orden.objects.count(), 1)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 9)

    def test_dos_clientes_ultima_unidad_sin_sobreventa(self):
        otro = CustomUser.objects.create_user(username='otro', password='Password123!')
        self.producto.stock = 1
        self.producto.save()
        CartService.add_item(self.cliente, self.producto.pk)
        CartService.add_item(otro, self.producto.pk)
        resultados = self.ejecutar_dos([lambda: OrdenService.checkout(self.cliente), lambda: OrdenService.checkout(otro)])
        self.assertCountEqual([r[0] for r in resultados], ['ok', 'rechazo'])
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 0)
        self.assertEqual(Orden.objects.count(), 1)

    def test_compras_de_distintos_productos_numeracion_unica(self):
        otro = CustomUser.objects.create_user(username='otro', password='Password123!')
        segundo = Producto.objects.create(nombre='GPU', sku='GPU', categoria=self.producto.categoria, marca=self.producto.marca, precio=200, stock=3)
        CartService.add_item(self.cliente, self.producto.pk)
        CartService.add_item(otro, segundo.pk)
        resultados = self.ejecutar_dos([lambda: OrdenService.checkout(self.cliente), lambda: OrdenService.checkout(otro)])
        self.assertEqual([r[0] for r in resultados], ['ok', 'ok'])
        self.assertEqual(len(set(Orden.objects.values_list('numero_orden', flat=True))), 2)

    def test_incrementos_simultaneos_no_se_pierden(self):
        CartService.get_or_create_cart(self.cliente)
        resultados = self.ejecutar_dos([lambda: CartService.add_item(self.cliente, self.producto.pk)] * 2)
        self.assertEqual([r[0] for r in resultados], ['ok', 'ok'])
        self.assertEqual(self.cliente.carrito.items.get().cantidad, 2)

    def test_cancelaciones_simultaneas_no_duplican_stock(self):
        CartService.add_item(self.cliente, self.producto.pk, 2)
        orden = OrdenService.checkout(self.cliente)
        resultados = self.ejecutar_dos([lambda: OrdenService.cambiar_estado_orden(orden.pk, 'CANCELADO')] * 2)
        self.assertCountEqual([r[0] for r in resultados], ['ok', 'rechazo'])
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 10)
