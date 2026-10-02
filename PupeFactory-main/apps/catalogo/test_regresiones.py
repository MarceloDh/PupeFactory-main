"""CRUD de atributos normalizados y navegación de catálogo con filtros."""
from django.test import TestCase
from rest_framework.test import APIClient
from apps.usuarios.models import CustomUser
from apps.catalogo.models import Categoria, Marca, Producto, EspecificacionProducto


class CatalogoRegresionesTest(TestCase):
    def setUp(self):
        self.categoria = Categoria.objects.create(nombre='CPU', slug='cpu')
        self.marca = Marca.objects.create(nombre='AMD', slug='amd')
        self.admin = CustomUser.objects.create_user(username='gestor', role='ADMINISTRADOR')
        self.api = APIClient()
        self.api.force_authenticate(self.admin)

    def test_crud_preserva_atributos_en_filas_y_baja_logica(self):
        response = self.api.post('/api/productos/', {
            'nombre': 'CPU', 'sku': 'CPU-1', 'categoria': self.categoria.pk,
            'marca': self.marca.pk, 'precio': '100.00', 'stock': 3,
            'especificaciones': {'Socket': 'AM5', 'Núcleos': '8'},
        }, format='json')
        self.assertEqual(response.status_code, 201, response.data)
        pk = response.data['id']
        self.assertEqual(EspecificacionProducto.objects.filter(producto_id=pk).count(), 2)
        response = self.api.patch(f'/api/productos/{pk}/', {'especificaciones': {'Socket': 'AM4'}}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['especificaciones'], {'Socket': 'AM4'})
        self.assertEqual(EspecificacionProducto.objects.filter(producto_id=pk).count(), 1)
        self.assertEqual(self.api.delete(f'/api/productos/{pk}/').status_code, 200)
        self.assertFalse(Producto.objects.get(pk=pk).activo)
        self.assertEqual(APIClient().get(f'/api/productos/{pk}/').status_code, 404)

    def test_paginacion_conserva_filtros_y_precio_se_aplica(self):
        for i in range(14):
            Producto.objects.create(nombre=f'CPU {i}', sku=f'CPU-{i}', categoria=self.categoria,
                                    marca=self.marca, precio=100, stock=1)
        response = self.client.get('/catalogo/?marca=amd&precio_min=50')
        self.assertContains(response, 'page=2')
        self.assertContains(response, 'marca=amd')
        response = self.client.get('/catalogo/?precio_min=1000')
        self.assertContains(response, 'No se encontraron productos')

    def test_especificaciones_se_muestran_en_ficha(self):
        producto = Producto.objects.create(nombre='CPU', sku='CPU', categoria=self.categoria,
                                           marca=self.marca, precio=100, stock=1, especificaciones={'Socket': 'AM5'})
        self.assertContains(self.client.get(f'/catalogo/{producto.pk}/'), 'AM5')

    def test_admin_desactiva_producto_vendido_sin_borrar_historial(self):
        from apps.carro.services import CartService
        from apps.ordenes.services import OrdenService
        from apps.ordenes.models import OrdenItem
        administrador = CustomUser.objects.create_superuser(username='supergestor', password='Password123!', role='ADMINISTRADOR')
        comprador = CustomUser.objects.create_user(username='comprador')
        producto = Producto.objects.create(nombre='CPU', sku='CPU', categoria=self.categoria,
                                           marca=self.marca, precio=100, stock=1)
        CartService.add_item(comprador, producto.pk)
        orden = OrdenService.checkout(comprador)
        self.client.force_login(administrador)
        response = self.client.get(f'/admin/catalogo/producto/{producto.pk}/delete/')
        self.assertContains(response, 'Desactivar producto')
        self.assertContains(response, 'Se conservan sus datos')
        response = self.client.post('/admin/catalogo/producto/', {
            'action': 'delete_selected', '_selected_action': [str(producto.pk)], 'index': '0'})
        self.assertContains(response, 'Desactivar productos')
        producto.refresh_from_db()
        self.assertTrue(producto.activo)
        response = self.client.post(f'/admin/catalogo/producto/{producto.pk}/delete/', {'post': 'yes'}, follow=True)
        self.assertEqual(response.status_code, 200)
        producto.refresh_from_db()
        self.assertFalse(producto.activo)
        self.assertTrue(OrdenItem.objects.filter(orden=orden, producto=producto).exists())
        publico = self.client_class()
        self.assertEqual(publico.get(f'/catalogo/{producto.pk}/').status_code, 404)
        stock = producto.stock
        response = self.client.post('/admin/catalogo/producto/', {
            'action': 'reactivar', '_selected_action': [str(producto.pk)], 'index': '0'}, follow=True)
        self.assertEqual(response.status_code, 200)
        producto.refresh_from_db()
        self.assertTrue(producto.activo)
        self.assertEqual(producto.stock, stock)
        self.assertTrue(OrdenItem.objects.filter(orden=orden, producto=producto).exists())
        self.assertEqual(publico.get(f'/catalogo/{producto.pk}/').status_code, 200)
        response = self.client.post('/admin/catalogo/producto/', {
            'action': 'delete_selected', '_selected_action': [str(producto.pk)], 'index': '0', 'post': 'yes'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'productos desactivados')
        producto.refresh_from_db()
        self.assertFalse(producto.activo)
        self.assertEqual(producto.stock, stock)
        self.assertTrue(OrdenItem.objects.filter(orden=orden, producto=producto).exists())
