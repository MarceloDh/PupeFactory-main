from django.test import TestCase, Client
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import UntypedToken
import jwt
from django.conf import settings
from apps.usuarios.models import CustomUser

# ==============================================================================
# SUITE DE PRUEBAS AUTOMATIZADAS - FASE 2: AUTENTICACIÓN, ROLES Y SWAGGER
# ==============================================================================
# Cubre exhaustivamente los 10 casos obligatorios solicitados:
# - JWT login y generación de tokens
# - Claims en payload (user_id, username, role)
# - Refresh token
# - Protección de Swagger y OpenAPI Schema por rol en backend
# - Login y Logout tradicional por sesiones Django
# ==============================================================================

class AutenticacionYPermisosTestCase(TestCase):

    def setUp(self):
        # Crear usuario Cliente
        self.cliente = CustomUser.objects.create_user(
            username='cliente_test',
            email='cliente@pupefactory.cl',
            password='Password123!',
            role=CustomUser.Role.CLIENTE
        )

        # Crear usuario Administrador
        self.admin = CustomUser.objects.create_user(
            username='admin_test',
            email='admin@pupefactory.cl',
            password='AdminPassword123!',
            role=CustomUser.Role.ADMINISTRADOR,
            is_staff=True
        )

        self.api_client = APIClient()
        self.web_client = Client()

    def test_caso_1_jwt_login_credenciales_correctas(self):
        """CASO 1: POST /api/auth/token/ con credenciales de cliente retorna 200, access y refresh."""
        url = reverse('token_obtain_pair')
        response = self.api_client.post(url, {
            'username': 'cliente_test',
            'password': 'Password123!'
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['user']['role'], CustomUser.Role.CLIENTE)

    def test_caso_2_jwt_payload_incluye_claims_de_rol(self):
        """CASO 2: Decodificar token cliente y verificar claims obligatorios: user_id, username, role."""
        url = reverse('token_obtain_pair')
        response = self.api_client.post(url, {
            'username': 'cliente_test',
            'password': 'Password123!'
        }, format='json')

        access_token = response.data['access']
        # Decodificar el token sin verificar firma para inspeccionar claims
        decoded_payload = jwt.decode(access_token, options={"verify_signature": False})

        self.assertEqual(decoded_payload['user_id'], self.cliente.id)
        self.assertEqual(decoded_payload['username'], 'cliente_test')
        self.assertEqual(decoded_payload['role'], CustomUser.Role.CLIENTE)

    def test_caso_3_jwt_refresh_token(self):
        """CASO 3: POST /api/auth/token/refresh/ genera un nuevo access token válido."""
        token_url = reverse('token_obtain_pair')
        login_res = self.api_client.post(token_url, {
            'username': 'cliente_test',
            'password': 'Password123!'
        }, format='json')
        refresh_token = login_res.data['refresh']

        refresh_url = reverse('token_refresh')
        response = self.api_client.post(refresh_url, {
            'refresh': refresh_token
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_caso_4_cliente_intenta_ver_swagger_docs(self):
        """CASO 4: Un cliente autenticado intenta entrar a /api/docs/ -> 403 Forbidden."""
        self.web_client.login(username='cliente_test', password='Password123!')
        response = self.web_client.get('/api/docs/')

        # Debe ser rechazado por backend con 403 Forbidden
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_caso_5_cliente_intenta_ver_schema_openapi(self):
        """CASO 5: Un cliente intenta consultar /api/schema/ -> 403 Forbidden."""
        self.web_client.login(username='cliente_test', password='Password123!')
        response = self.web_client.get('/api/schema/')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_caso_6_admin_visita_swagger_docs(self):
        """CASO 6: Un administrador autenticado visita /api/docs/ -> 200 OK con Swagger UI."""
        self.web_client.login(username='admin_test', password='AdminPassword123!')
        response = self.web_client.get('/api/docs/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'swagger-ui')

    def test_caso_7_admin_visita_schema_openapi(self):
        """CASO 7: Un administrador visita /api/schema/ -> 200 OK con esquema OpenAPI."""
        self.web_client.login(username='admin_test', password='AdminPassword123!')
        response = self.web_client.get('/api/schema/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_caso_8_anonimo_visita_documentacion(self):
        """CASO 8: Usuario anónimo no autenticado visita Swagger o Schema -> Denegado (401 o 403)."""
        response_docs = self.web_client.get('/api/docs/')
        self.assertIn(response_docs.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

        response_schema = self.web_client.get('/api/schema/')
        self.assertIn(response_schema.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_caso_9_login_html_cliente(self):
        """CASO 9: Login HTML tradicional crea la sesión web y autentica a request.user."""
        response = self.web_client.post(reverse('login'), {
            'username': 'cliente_test',
            'password': 'Password123!'
        }, follow=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verificar que el usuario quedó autenticado en la sesión mediante request.user
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertEqual(response.wsgi_request.user.role, CustomUser.Role.CLIENTE)

    def test_caso_10_logout_html(self):
        """CASO 10: Logout HTML tradicional termina la sesión de forma limpia."""
        self.web_client.login(username='cliente_test', password='Password123!')
        response = self.web_client.post(reverse('logout'), follow=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_credenciales_invalidas_retornan_401_limpio(self):
        """Prueba adicional: Credenciales erróneas en JWT retornan 401 sin exponer trazas técnicas."""
        url = reverse('token_obtain_pair')
        response = self.api_client.post(url, {
            'username': 'cliente_test',
            'password': 'PasswordEquivocada!'
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('status', response.data)
        self.assertEqual(response.data['status'], 401)

    # ==========================================================================
    # PRUEBAS DE REGISTRO DE CUENTA (CREAR CUENTA / CHECKOUT INVITATION)
    # ==========================================================================

    def test_registro_web_exitoso_y_autologin(self):
        """El registro web crea un usuario con rol CLIENTE y lo loguea automáticamente."""
        url = reverse('register')
        data = {
            'username': 'nuevo_cliente',
            'email': 'nuevo@pupefactory.cl',
            'first_name': 'Carlos',
            'last_name': 'González',
            'password': 'PasswordSegura123!',
            'password_confirm': 'PasswordSegura123!',
        }
        response = self.web_client.post(url, data, follow=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verificar que el usuario fue creado en la base de datos
        user = CustomUser.objects.get(username='nuevo_cliente')
        self.assertEqual(user.email, 'nuevo@pupefactory.cl')
        self.assertEqual(user.first_name, 'Carlos')
        self.assertEqual(user.role, CustomUser.Role.CLIENTE)
        self.assertTrue(user.check_password('PasswordSegura123!'))

        # Verificar autologin en sesión
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertEqual(response.wsgi_request.user.username, 'nuevo_cliente')

    def test_registro_web_redireccion_checkout(self):
        """El registro web preserva el parámetro next=/checkout/ y redirige al flujo de pago."""
        url = f"{reverse('register')}?next=/checkout/"
        # Comprobar que en GET se muestra el banner de invitación a pago
        get_res = self.web_client.get(url)
        self.assertEqual(get_res.status_code, status.HTTP_200_OK)
        self.assertContains(get_res, "¡Estás a un paso de completar tu compra!")

        data = {
            'username': 'comprador_directo',
            'email': 'comprador@pupefactory.cl',
            'first_name': 'Ana',
            'last_name': 'Reyes',
            'password': 'PasswordSegura123!',
            'password_confirm': 'PasswordSegura123!',
            'next': '/checkout/',
        }
        post_res = self.web_client.post(url, data, follow=False)
        # Debe redirigir directamente a /checkout/
        self.assertEqual(post_res.status_code, status.HTTP_302_FOUND)
        self.assertEqual(post_res.url, '/checkout/')

    def test_login_muestra_banner_invitacion_checkout(self):
        """Al ingresar a login con next=/checkout/, se invita a loguearse o crear cuenta."""
        url = f"{reverse('login')}?next=/checkout/"
        response = self.web_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "¡Estás a un paso de completar tu compra!")
        self.assertContains(response, "crea una cuenta nueva aquí")
        self.assertContains(response, "Crear Cuenta Gratuita")

    def test_registro_web_error_passwords_no_coinciden(self):
        """El registro rechaza si password y password_confirm difieren."""
        url = reverse('register')
        data = {
            'username': 'error_pwd',
            'email': 'error@pupefactory.cl',
            'password': 'PasswordSegura123!',
            'password_confirm': 'PasswordDiferente999!',
        }
        response = self.web_client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(CustomUser.objects.filter(username='error_pwd').exists())
        self.assertContains(response, "Las contraseñas no coinciden.")

    def test_registro_web_error_username_duplicado(self):
        """El registro rechaza usernames ya registrados."""
        url = reverse('register')
        data = {
            'username': 'cliente_test',  # Ya creado en setUp
            'email': 'otro_correo@pupefactory.cl',
            'password': 'PasswordSegura123!',
            'password_confirm': 'PasswordSegura123!',
        }
        response = self.web_client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "Este nombre de usuario ya se encuentra registrado.")

    def test_registro_api_exitoso(self):
        """POST /api/auth/register/ crea el usuario CLIENTE y retorna tokens JWT."""
        url = reverse('api_register')
        data = {
            'username': 'api_user',
            'email': 'api@pupefactory.cl',
            'first_name': 'Mario',
            'last_name': 'Silva',
            'password': 'PasswordSegura123!',
            'password_confirm': 'PasswordSegura123!',
        }
        response = self.api_client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
        self.assertIn('refresh', response.data['tokens'])
        self.assertEqual(response.data['user']['role'], CustomUser.Role.CLIENTE)

        # Verificar que el usuario existe en base de datos
        self.assertTrue(CustomUser.objects.filter(username='api_user').exists())

    def test_registro_api_error_validacion(self):
        """POST /api/auth/register/ rechaza peticiones con datos incompletos o inválidos."""
        url = reverse('api_register')
        data = {
            'username': 'api_user',
            'email': 'not-an-email',
            'password': '123',  # demasiado corta
            'password_confirm': '456',
        }
        response = self.api_client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

