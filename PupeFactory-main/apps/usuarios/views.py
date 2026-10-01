from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.views import View
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.http import url_has_allowed_host_and_scheme
from drf_spectacular.utils import extend_schema, OpenApiResponse

from apps.usuarios.forms import UsuarioRegistroForm
from apps.usuarios.serializers import (
    CustomTokenObtainPairSerializer,
    RegistroSerializer,
)

# ==============================================================================
# VISTAS DE AUTENTICACIÓN API (JWT)
# ==============================================================================

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Endpoint POST /api/auth/token/
    Recibe username y password, devuelve access y refresh tokens
    con los claims personalizados de user_id, username y role.
    """
    serializer_class = CustomTokenObtainPairSerializer


class RegistroAPIView(APIView):
    """
    Endpoint POST /api/auth/register/
    Permite registrar un nuevo usuario con rol CLIENTE mediante la API REST.
    Devuelve los datos del nuevo usuario y los tokens JWT generados.
    """
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="Registro de nuevo cliente",
        description="Crea una cuenta de usuario con rol CLIENTE. Retorna información del usuario y tokens JWT.",
        request=RegistroSerializer,
        responses={
            201: OpenApiResponse(description="Usuario registrado exitosamente"),
            400: OpenApiResponse(description="Errores de validación en campos o contraseñas"),
        },
        tags=["Autenticación"],
    )
    def post(self, request):
        serializer = RegistroSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            refresh['user_id'] = user.id
            refresh['username'] = user.username
            refresh['role'] = user.role

            return Response({
                'message': 'Usuario registrado exitosamente',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'role': user.role,
                },
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ==============================================================================
# VISTAS DE AUTENTICACIÓN WEB (SESIONES DJANGO TEMPLATES)
# ==============================================================================

class UsuarioLoginView(LoginView):
    """
    Vista de inicio de sesión web tradicional mediante Django Sessions.
    Utiliza el mismo modelo CustomUser que la API REST.
    Redirige al parámetro next (ej: /checkout/) o LOGIN_REDIRECT_URL tras éxito.
    """
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        next_url = self.request.GET.get('next') or self.request.POST.get('next', '')
        context['next'] = next_url
        context['is_checkout_redirect'] = bool(next_url and ('checkout' in next_url or 'carro' in next_url))
        return context

    def form_invalid(self, form):
        messages.error(self.request, "Credenciales incorrectas. Verifique su usuario y contraseña.")
        return super().form_invalid(form)


class UsuarioRegistroView(View):
    """
    Vista web para el registro de nuevos clientes.
    Tras crear la cuenta exitosamente, inicia sesión automáticamente al usuario
    y lo redirige a la URL de destino (ej. /checkout/ para completar su compra).
    """
    template_name = 'accounts/register.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('catalogo')
        form = UsuarioRegistroForm()
        next_url = request.GET.get('next', '')
        is_checkout_redirect = bool(next_url and ('checkout' in next_url or 'carro' in next_url))
        return render(request, self.template_name, {
            'form': form,
            'next': next_url,
            'is_checkout_redirect': is_checkout_redirect,
        })

    def post(self, request):
        if request.user.is_authenticated:
            return redirect('catalogo')
        form = UsuarioRegistroForm(request.POST)
        next_url = request.POST.get('next') or request.GET.get('next', '')
        if form.is_valid():
            user = form.save()
            login(request, user)
            nombre = user.first_name if user.first_name else user.username
            messages.success(request, f"¡Bienvenido a PupeFactory, {nombre}! Tu cuenta ha sido creada exitosamente.")

            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                return redirect(next_url)
            return redirect('catalogo')

        is_checkout_redirect = bool(next_url and ('checkout' in next_url or 'carro' in next_url))
        return render(request, self.template_name, {
            'form': form,
            'next': next_url,
            'is_checkout_redirect': is_checkout_redirect,
        })


class UsuarioLogoutView(LogoutView):
    """
    Vista de cierre de sesión web tradicional.
    Elimina la sesión del usuario en la base de datos de PostgreSQL.
    """
    next_page = reverse_lazy('login')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, "Has cerrado sesión correctamente.")
        return super().dispatch(request, *args, **kwargs)

