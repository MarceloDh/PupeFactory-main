from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from apps.catalogo.models import Categoria, Marca, Producto
from apps.carro.models import Carrito
from apps.carro.services import CartService
from apps.ordenes.models import Orden, OrdenItem
from apps.ordenes.services import OrdenService
from apps.usuarios.models import CustomUser


class OrdenesTestCase(TestCase):
    """
    Suite de pruebas completa para FASE 5 — Checkout, Órdenes, Stock Atómico y Gestión de Estados.
    Cubre:
    1. Checkout y creación de orden histórica.
    2. Congelamiento inmutable de precios (3FN).
    3. Control y descuento atómico de stock (transaction.atomic + select_for_update).
    4. Concurrencia y prevención de sobreventa / stock negativo.
    5. Máquina de estados (PENDIENTE, PAGADO, ENTREGADO, CANCELADO).
    6. Cancelación con reposición atómica de stock y control anti-duplicidad.
    7. Seguridad RBAC y aislamiento estricto anti-IDOR.
    8. Interfaz web tradicional (vistas Django, redirecciones y confirmación).
    """

    def setUp(self):
        # 1. Catálogo base
        self.categoria = Categoria.objects.create(nombre='Procesadores', slug='procesadores')
        self.marca_amd = Marca.objects.create(nombre='AMD', slug='amd')
        self.marca_nvidia = Marca.objects.create(nombre='NVIDIA', slug='nvidia')

        self.prod_cpu = Producto.objects.create(
            nombre='Ryzen 7 7800X3D',
            sku='CPU-AMD-7800X3D',
            categoria=self.categoria,
            marca=self.marca_amd,
            precio=Decimal('420000.00'),
            stock=5,
            activo=True
        )

        self.prod_gpu = Producto.objects.create(
            nombre='GeForce RTX 5070',
            sku='GPU-NV-5070',
            categoria=self.categoria,
            marca=self.marca_nvidia,
            precio=Decimal('600000.00'),
            stock=1,  # Stock limitado para pruebas de concurrencia
            activo=True
        )

        self.prod_inactivo = Producto.objects.create(
            nombre='Componente Descontinuado',
            sku='OLD-PART-01',
            categoria=self.categoria,
            marca=self.marca_amd,
            precio=Decimal('50000.00'),
            stock=10,
            activo=False
        )

        # 2. Usuarios con roles
        self.cliente_a = CustomUser.objects.create_user(
            username='cliente_a',
            email='clientea@pupefactory.cl',
            password='Password123!',
            role=CustomUser.Role.CLIENTE
        )

        self.cliente_b = CustomUser.objects.create_user(
            username='cliente_b',
            email='clienteb@pupefactory.cl',
            password='Password123!',
            role=CustomUser.Role.CLIENTE
        )

        self.admin_user = CustomUser.objects.create_user(
            username='admin_user',
            email='admin@pupefactory.cl',
            password='AdminPassword123!',
            role=CustomUser.Role.ADMINISTRADOR,
            is_staff=True
        )

        # 3. Clientes API DRF
        self.client_anon = APIClient()

        self.client_a = APIClient()
        self.client_a.force_authenticate(user=self.cliente_a)

        self.client_b = APIClient()
        self.client_b.force_authenticate(user=self.cliente_b)

        self.client_admin = APIClient()
        self.client_admin.force_authenticate(user=self.admin_user)

        # 4. Clientes Web (Django Session)
        self.web_client_a = Client()
        self.web_client_a.login(username='cliente_a', password='Password123!')

        # URLs API
        self.url_checkout = reverse('api_checkout')
        self.url_mis_ordenes = reverse('api_mis_ordenes')

    # --------------------------------------------------------------------------
    # 1. CHECKOUT Y CREACIÓN DE ÓRDENES
    # --------------------------------------------------------------------------
    def test_01_checkout_carrito_vacio_rechaza_compra(self):
        """1. Checkout con carro vacío rechaza la compra con HTTP 400."""
        response = self.client_a.post(self.url_checkout)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("vacío", response.data['error'])
        self.assertEqual(Orden.objects.count(), 0)

    def test_02_checkout_exitoso_crea_orden(self):
        """2. Checkout con productos válidos crea la Orden en estado PAGADO con total correcto."""
        CartService.add_item(self.cliente_a, self.prod_cpu.id, cantidad=2)
        response = self.client_a.post(self.url_checkout)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.data
        self.assertEqual(data['estado'], 'PAGADO')
        self.assertEqual(Decimal(data['total']), Decimal('840000.00'))
        self.assertEqual(len(data['items']), 1)
        self.assertEqual(data['items'][0]['cantidad'], 2)
        self.assertEqual(Decimal(data['items'][0]['precio_unitario']), Decimal('420000.00'))
        self.assertEqual(Orden.objects.count(), 1)

    def test_03_checkout_vacia_carrito(self):
        """3. Al completar una compra exitosa, el carro persistente queda vacío."""
        CartService.add_item(self.cliente_a, self.prod_cpu.id, cantidad=1)
        carrito = CartService.get_or_create_cart(self.cliente_a)
        self.assertEqual(carrito.items.count(), 1)

        response = self.client_a.post(self.url_checkout)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        carrito.refresh_from_db()
        self.assertEqual(carrito.items.count(), 0)
        # La instancia Carrito continúa existiendo
        self.assertTrue(Carrito.objects.filter(usuario=self.cliente_a).exists())

    # --------------------------------------------------------------------------
    # 2. STOCK ATÓMICO Y DESCUENTO
    # --------------------------------------------------------------------------
    def test_04_checkout_disminuye_stock_correctamente(self):
        """4. El stock del producto disminuye exactamente en la cantidad comprada."""
        stock_inicial = self.prod_cpu.stock  # 5
        CartService.add_item(self.cliente_a, self.prod_cpu.id, cantidad=3)

        self.client_a.post(self.url_checkout)

        self.prod_cpu.refresh_from_db()
        self.assertEqual(self.prod_cpu.stock, stock_inicial - 3)  # 2

    def test_05_checkout_stock_insuficiente_cancela_transaccion(self):
        """5. Si el stock no alcanza al momento del checkout, se cancela la transacción atómica."""
        CartService.add_item(self.cliente_a, self.prod_cpu.id, cantidad=4)
        # Reducción externa de stock antes de comprar
        self.prod_cpu.stock = 2
        self.prod_cpu.save(update_fields=['stock'])

        response = self.client_a.post(self.url_checkout)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Stock insuficiente", response.data['error'])

        # No se crea ninguna orden
        self.assertEqual(Orden.objects.count(), 0)
        # El stock físico no varía
        self.prod_cpu.refresh_from_db()
        self.assertEqual(self.prod_cpu.stock, 2)

    def test_06_checkout_stock_nunca_queda_negativo(self):
        """6. El stock nunca puede llegar a un valor negativo."""
        self.prod_gpu.stock = 1
        self.prod_gpu.save()

        CartService.add_item(self.cliente_a, self.prod_gpu.id, cantidad=1)
        CartService.add_item(self.cliente_b, self.prod_gpu.id, cantidad=1)

        # Compra Cliente A
        res_a = self.client_a.post(self.url_checkout)
        self.assertEqual(res_a.status_code, status.HTTP_201_CREATED)

        # Compra Cliente B
        res_b = self.client_b.post(self.url_checkout)
        self.assertEqual(res_b.status_code, status.HTTP_400_BAD_REQUEST)

        self.prod_gpu.refresh_from_db()
        self.assertEqual(self.prod_gpu.stock, 0)
        self.assertGreaterEqual(self.prod_gpu.stock, 0)

    # --------------------------------------------------------------------------
    # 3. PRECIO HISTÓRICO CONGELADO (3FN)
    # --------------------------------------------------------------------------
    def test_07_precio_historico_congelado_3fn(self):
        """7. OrdenItem congela el precio unitario del producto al momento de comprar (3FN)."""
        CartService.add_item(self.cliente_a, self.prod_cpu.id, cantidad=1)
        res = self.client_a.post(self.url_checkout)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        item_orden = OrdenItem.objects.first()
        self.assertEqual(item_orden.precio_unitario, Decimal('420000.00'))

        # Modificación posterior de precio en el catálogo
        self.prod_cpu.precio = Decimal('650000.00')
        self.prod_cpu.save(update_fields=['precio'])

        # El detalle de la orden antigua mantiene su precio congelado
        item_orden.refresh_from_db()
        self.assertEqual(item_orden.precio_unitario, Decimal('420000.00'))
        self.assertEqual(item_orden.subtotal, Decimal('420000.00'))

    # --------------------------------------------------------------------------
    # 4. CONCURRENCIA Y BLOQUEO PESIMISTA (SELECT_FOR_UPDATE)
    # --------------------------------------------------------------------------
    def test_08_dos_compras_secuenciales_ultima_unidad(self):
        """8. Compras secuenciales: una compra y el siguiente intento se rechaza."""
        self.prod_gpu.stock = 1
        self.prod_gpu.save()

        CartService.add_item(self.cliente_a, self.prod_gpu.id, cantidad=1)
        CartService.add_item(self.cliente_b, self.prod_gpu.id, cantidad=1)

        # La concurrencia real se cubre en test_regresiones con PostgreSQL.
        res1 = self.client_a.post(self.url_checkout)
        res2 = self.client_b.post(self.url_checkout)

        self.assertEqual(res1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res2.status_code, status.HTTP_400_BAD_REQUEST)

        self.prod_gpu.refresh_from_db()
        self.assertEqual(self.prod_gpu.stock, 0)
        self.assertEqual(Orden.objects.count(), 1)

    # --------------------------------------------------------------------------
    # 5. GESTIÓN DE ESTADOS Y REPOSICIÓN DE STOCK
    # --------------------------------------------------------------------------
    def test_09_cancelacion_orden_devuelve_stock(self):
        """9. Cancelar una orden pagada devuelve las unidades compradas al stock físico."""
        CartService.add_item(self.cliente_a, self.prod_cpu.id, cantidad=2)
        res = self.client_a.post(self.url_checkout)
        orden_id = res.data['id']

        self.prod_cpu.refresh_from_db()
        self.assertEqual(self.prod_cpu.stock, 3)

        # Admin cambia estado a CANCELADO
        url_estado = reverse('api_orden_estado', kwargs={'pk': orden_id})
        res_patch = self.client_admin.patch(url_estado, {'estado': 'CANCELADO'}, format='json')

        self.assertEqual(res_patch.status_code, status.HTTP_200_OK)
        self.assertEqual(res_patch.data['estado'], 'CANCELADO')
        self.assertTrue(res_patch.data['stock_reincorporado'])

        # Stock restituido a 5
        self.prod_cpu.refresh_from_db()
        self.assertEqual(self.prod_cpu.stock, 5)

    def test_10_cancelacion_evita_doble_reposicion(self):
        """10. El control atómico stock_reincorporado impide dobles devoluciones de stock."""
        CartService.add_item(self.cliente_a, self.prod_cpu.id, cantidad=2)
        res = self.client_a.post(self.url_checkout)
        orden = Orden.objects.get(id=res.data['id'])

        # Primera cancelación
        OrdenService.cambiar_estado_orden(orden.id, Orden.Estado.CANCELADO)
        self.prod_cpu.refresh_from_db()
        self.assertEqual(self.prod_cpu.stock, 5)
        orden.refresh_from_db()
        self.assertTrue(orden.stock_reincorporado)

        # Intento de forzar transición sobre estado terminal o re-ejecución
        with self.assertRaises(Exception):
            OrdenService.cambiar_estado_orden(orden.id, Orden.Estado.CANCELADO)

        # El stock sigue en 5, no se duplica
        self.prod_cpu.refresh_from_db()
        self.assertEqual(self.prod_cpu.stock, 5)

    def test_11_transicion_a_entregado_no_modifica_stock(self):
        """11. Cambiar una orden de PAGADO a ENTREGADO no altera el inventario."""
        CartService.add_item(self.cliente_a, self.prod_cpu.id, cantidad=1)
        res = self.client_a.post(self.url_checkout)
        orden_id = res.data['id']

        self.prod_cpu.refresh_from_db()
        self.assertEqual(self.prod_cpu.stock, 4)

        url_estado = reverse('api_orden_estado', kwargs={'pk': orden_id})
        res_patch = self.client_admin.patch(url_estado, {'estado': 'ENTREGADO'}, format='json')

        self.assertEqual(res_patch.status_code, status.HTTP_200_OK)
        self.assertEqual(res_patch.data['estado'], 'ENTREGADO')

        self.prod_cpu.refresh_from_db()
        self.assertEqual(self.prod_cpu.stock, 4)

    def test_12_transicion_invalida_rechazada(self):
        """12. Una transición inválida en la máquina de estados retorna HTTP 400."""
        CartService.add_item(self.cliente_a, self.prod_cpu.id, cantidad=1)
        res = self.client_a.post(self.url_checkout)
        orden_id = res.data['id']

        # CANCELADO es estado terminal definitivo
        OrdenService.cambiar_estado_orden(orden_id, Orden.Estado.CANCELADO)

        url_estado = reverse('api_orden_estado', kwargs={'pk': orden_id})
        res_patch = self.client_admin.patch(url_estado, {'estado': 'PAGADO'}, format='json')
        self.assertEqual(res_patch.status_code, status.HTTP_400_BAD_REQUEST)

    def test_12_b_devolucion_orden_entregada_repone_stock(self):
        """12b. Cancelar o procesar devolución de una orden entregada devuelve el stock físico."""
        CartService.add_item(self.cliente_a, self.prod_cpu.id, cantidad=1)
        res = self.client_a.post(self.url_checkout)
        orden_id = res.data['id']

        # Transicionar a ENTREGADO
        OrdenService.cambiar_estado_orden(orden_id, Orden.Estado.ENTREGADO)
        self.prod_cpu.refresh_from_db()
        self.assertEqual(self.prod_cpu.stock, 4)

        # Admin procesa devolución / cancelación
        url_estado = reverse('api_orden_estado', kwargs={'pk': orden_id})
        res_patch = self.client_admin.patch(url_estado, {'estado': 'CANCELADO'}, format='json')
        self.assertEqual(res_patch.status_code, status.HTTP_200_OK)
        self.assertEqual(res_patch.data['estado'], 'CANCELADO')
        self.assertTrue(res_patch.data['stock_reincorporado'])

        # Stock restituido al catálogo
        self.prod_cpu.refresh_from_db()
        self.assertEqual(self.prod_cpu.stock, 5)

    # --------------------------------------------------------------------------
    # 6. HISTORIAL Y SEGURIDAD ANTI-IDOR
    # --------------------------------------------------------------------------
    def test_13_mis_ordenes_cliente_aislamiento_anti_idor(self):
        """13. Un cliente solo puede ver sus propias órdenes, nunca las de otros clientes (Anti-IDOR)."""
        CartService.add_item(self.cliente_a, self.prod_cpu.id, cantidad=1)
        res_a = self.client_a.post(self.url_checkout)
        orden_a_id = res_a.data['id']

        # Cliente B consulta su historial
        res_hist_b = self.client_b.get(self.url_mis_ordenes)
        self.assertEqual(res_hist_b.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res_hist_b.data), 0)

        # Cliente B intenta ver directamente la orden de Cliente A (IDOR)
        url_detalle = reverse('api_mi_orden_detalle', kwargs={'pk': orden_a_id})
        res_idor = self.client_b.get(url_detalle)
        self.assertEqual(res_idor.status_code, status.HTTP_404_NOT_FOUND)

    def test_14_cliente_no_puede_cambiar_estados(self):
        """14. Un cliente no tiene autorización para cambiar estados de orden (HTTP 403)."""
        CartService.add_item(self.cliente_a, self.prod_cpu.id, cantidad=1)
        res = self.client_a.post(self.url_checkout)
        orden_id = res.data['id']

        url_estado = reverse('api_orden_estado', kwargs={'pk': orden_id})
        res_cliente = self.client_a.patch(url_estado, {'estado': 'CANCELADO'}, format='json')
        self.assertEqual(res_cliente.status_code, status.HTTP_403_FORBIDDEN)

    def test_15_anonimo_checkout_retorna_401(self):
        """15. Usuario no autenticado recibe 401 en checkout."""
        res = self.client_anon.post(self.url_checkout)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_16_anonimo_mis_ordenes_retorna_401(self):
        """16. Usuario no autenticado recibe 401 al consultar órdenes."""
        res = self.client_anon.get(self.url_mis_ordenes)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_17_administrador_checkout_retorna_403(self):
        """17. Administrador recibe 403 al intentar hacer checkout reservado a clientes."""
        res = self.client_admin.post(self.url_checkout)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_18_administrador_puede_cambiar_estados(self):
        """18. Administrador autenticado puede actualizar estados legítimamente."""
        CartService.add_item(self.cliente_a, self.prod_cpu.id, cantidad=1)
        res = self.client_a.post(self.url_checkout)
        orden_id = res.data['id']

        url_estado = reverse('api_orden_estado', kwargs={'pk': orden_id})
        res_admin = self.client_admin.patch(url_estado, {'estado': 'ENTREGADO'}, format='json')
        self.assertEqual(res_admin.status_code, status.HTTP_200_OK)
        self.assertEqual(res_admin.data['estado'], 'ENTREGADO')

    def test_19_producto_inactivo_rechaza_checkout(self):
        """19. Si un producto en carro es desactivado por admin antes de comprar, se rechaza el checkout."""
        CartService.add_item(self.cliente_a, self.prod_cpu.id, cantidad=1)
        self.prod_cpu.activo = False
        self.prod_cpu.save(update_fields=['activo'])

        res = self.client_a.post(self.url_checkout)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("no está disponible", res.data['error'])

    # --------------------------------------------------------------------------
    # 7. INTEGRACIÓN WEB (DJANGO TEMPLATES / SESSIONS)
    # --------------------------------------------------------------------------
    def test_20_web_checkout_get_muestra_resumen(self):
        """20. Vista web GET /checkout/ muestra los productos del carro y total a pagar."""
        CartService.add_item(self.cliente_a, self.prod_cpu.id, cantidad=2)
        response = self.web_client_a.get(reverse('checkout'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Confirmación de Orden y Pago')
        self.assertContains(response, 'Ryzen 7 7800X3D')
        self.assertContains(response, '840000')

    def test_21_web_checkout_vacio_redirige_a_carro(self):
        """21. Vista web GET /checkout/ con carro vacío redirige a /carro/ con alerta."""
        response = self.web_client_a.get(reverse('checkout'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('carro_detalle'))
        self.assertContains(response, 'Tu carro de compras está vacío')

    def test_22_web_checkout_post_procesa_compra_y_redirige(self):
        """22. Formulario web POST /checkout/ procesa la compra atómica y redirige a confirmación."""
        CartService.add_item(self.cliente_a, self.prod_cpu.id, cantidad=1)
        response = self.web_client_a.post(reverse('checkout'), follow=True)

        self.assertEqual(response.status_code, 200)
        orden = Orden.objects.first()
        self.assertRedirects(response, reverse('checkout_exito', kwargs={'orden_id': orden.id}))
        self.assertContains(response, '¡Compra realizada correctamente!')
        self.assertContains(response, orden.numero_orden)

    def test_23_web_checkout_exito_muestra_numero_orden(self):
        """23. Pantalla de éxito muestra explícitamente el número de orden correlativo (#0001)."""
        CartService.add_item(self.cliente_a, self.prod_cpu.id, cantidad=1)
        orden = OrdenService.checkout(self.cliente_a)

        response = self.web_client_a.get(reverse('checkout_exito', kwargs={'orden_id': orden.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Número de orden:')
        self.assertContains(response, orden.numero_orden)
        self.assertContains(response, orden.get_estado_display())

    def test_24_web_mis_ordenes_muestra_historial(self):
        """24. Vista web /mis-ordenes/ lista el historial del cliente autenticado con total y estado."""
        CartService.add_item(self.cliente_a, self.prod_cpu.id, cantidad=1)
        orden = OrdenService.checkout(self.cliente_a)

        response = self.web_client_a.get(reverse('mis_ordenes'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Mis Compras')
        self.assertContains(response, orden.numero_orden)
        self.assertContains(response, 'Ryzen 7 7800X3D')
        self.assertContains(response, '420000')
