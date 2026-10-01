from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError as DRFValidationError
from drf_spectacular.utils import extend_schema, OpenApiResponse

from apps.ordenes.models import Orden
from apps.ordenes.services import OrdenService
from apps.ordenes.serializers import (
    OrdenSerializer,
    CambiarEstadoOrdenSerializer,
)
from apps.carro.services import CartService
from apps.usuarios.permissions import IsClienteRole, IsAdminRole
from apps.usuarios.models import CustomUser


# ==============================================================================
# CONTROLADORES DE LA API REST (DRF - SIMPLE JWT)
# ==============================================================================

class CheckoutAPIView(APIView):
    """
    Endpoint para procesar el checkout de la compra del cliente autenticado.
    Transforma el carro en una orden, descuenta stock de forma atómica con select_for_update
    y vacía el carro persistente.
    """
    permission_classes = [IsClienteRole]

    @extend_schema(
        summary="Realizar compra (Checkout)",
        description=(
            "Procesa la compra a partir del carro persistente del cliente autenticado. "
            "Aplica transacciones atómicas (transaction.atomic), bloqueos pesimistas "
            "(select_for_update) para evitar sobreventa concurrente, descuenta el stock "
            "físico, congela los precios históricos (3FN) y vacía el carro."
        ),
        request=None,
        responses={
            201: OrdenSerializer,
            400: OpenApiResponse(description="Carro vacío, producto inactivo o stock insuficiente."),
            401: OpenApiResponse(description="Autenticación requerida."),
            403: OpenApiResponse(description="Acceso exclusivo para rol CLIENTE."),
        }
    )
    def post(self, request):
        orden = OrdenService.checkout(request.user)
        serializer = OrdenSerializer(orden)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MisOrdenesAPIView(APIView):
    """
    Endpoint para consultar el historial de órdenes del cliente autenticado.
    Protección estricta anti-IDOR: Solo retorna compras pertenecientes a request.user.
    """
    permission_classes = [IsClienteRole]

    @extend_schema(
        summary="Historial de órdenes del cliente",
        description="Retorna el listado cronológico de órdenes históricas realizadas por el cliente autenticado.",
        responses={
            200: OrdenSerializer(many=True),
            401: OpenApiResponse(description="Autenticación requerida."),
            403: OpenApiResponse(description="Acceso exclusivo para rol CLIENTE."),
        }
    )
    def get(self, request):
        ordenes = (
            Orden.objects.filter(usuario=request.user)
            .prefetch_related('items__producto')
            .order_by('-creado_en')
        )
        serializer = OrdenSerializer(ordenes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MiOrdenDetalleAPIView(APIView):
    """
    Endpoint para ver el detalle de una orden específica del cliente autenticado.
    Evita acceso horizontal (IDOR) validando explícitamente usuario=request.user.
    """
    permission_classes = [IsClienteRole]

    @extend_schema(
        summary="Detalle de una orden específica del cliente",
        description="Retorna el detalle completo con precios históricos de una orden del cliente autenticado.",
        responses={
            200: OrdenSerializer,
            401: OpenApiResponse(description="Autenticación requerida."),
            403: OpenApiResponse(description="Acceso exclusivo para rol CLIENTE."),
            404: OpenApiResponse(description="Orden no encontrada o no pertenece al usuario."),
        }
    )
    def get(self, request, pk):
        orden = get_object_or_404(
            Orden.objects.prefetch_related('items__producto'),
            pk=pk,
            usuario=request.user
        )
        serializer = OrdenSerializer(orden)
        return Response(serializer.data, status=status.HTTP_200_OK)


class OrdenEstadoAPIView(APIView):
    """
    Endpoint administrativo para la gestión de estados de orden.
    Aplica la máquina de estados del negocio y la reposición de stock al cancelar.
    """
    permission_classes = [IsAdminRole]

    @extend_schema(
        summary="Cambiar estado de una orden (Administrador)",
        description=(
            "Permite transicionar el estado de una orden (ej: PAGADO -> ENTREGADO, PAGADO -> CANCELADO). "
            "Al cancelar una orden pagada, devuelve atómicamente los productos al stock físico "
            "y marca stock_reincorporado=True para impedir dobles devoluciones."
        ),
        request=CambiarEstadoOrdenSerializer,
        responses={
            200: OrdenSerializer,
            400: OpenApiResponse(description="Transición de estado inválida."),
            401: OpenApiResponse(description="Autenticación requerida."),
            403: OpenApiResponse(description="Acceso exclusivo para administradores."),
            404: OpenApiResponse(description="Orden no encontrada."),
        }
    )
    def patch(self, request, pk):
        serializer = CambiarEstadoOrdenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        nuevo_estado = serializer.validated_data['estado']

        orden = OrdenService.cambiar_estado_orden(pk, nuevo_estado, request.user)
        return Response(OrdenSerializer(orden).data, status=status.HTTP_200_OK)


class OrdenListAdminAPIView(APIView):
    """
    Endpoint administrativo para listar todas las órdenes del sistema con fines de gestión.
    """
    permission_classes = [IsAdminRole]

    @extend_schema(
        summary="Listado global de órdenes (Administrador)",
        description="Retorna todas las órdenes registradas en el sistema para gestión de inventario y despacho.",
        responses={
            200: OrdenSerializer(many=True),
            401: OpenApiResponse(description="Autenticación requerida."),
            403: OpenApiResponse(description="Acceso exclusivo para administradores."),
        }
    )
    def get(self, request):
        ordenes = (
            Orden.objects.all()
            .prefetch_related('items__producto', 'usuario')
            .order_by('-creado_en')
        )
        serializer = OrdenSerializer(ordenes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ==============================================================================
# VISTAS WEB TRADICIONALES (DJANGO SESSIONS - COOKIE AUTHENTICATION)
# ==============================================================================

class CheckoutWebView(LoginRequiredMixin, View):
    """
    Vista web para la pantalla de revisión y confirmación del checkout.
    """
    login_url = 'login'

    def get(self, request):
        if request.user.role != CustomUser.Role.CLIENTE:
            messages.error(request, "Solo los clientes pueden realizar compras.")
            return redirect('catalogo')

        carrito = CartService.get_or_create_cart(request.user)
        if carrito.items.count() == 0:
            messages.warning(request, "Tu carro de compras está vacío. Agrega componentes antes de proceder al checkout.")
            return redirect('carro_detalle')

        return render(request, 'ordenes/checkout.html', {'carrito': carrito})

    def post(self, request):
        if request.user.role != CustomUser.Role.CLIENTE:
            messages.error(request, "Solo los clientes pueden realizar compras.")
            return redirect('catalogo')

        try:
            orden = OrdenService.checkout(request.user)
            messages.success(request, f"¡Compra realizada con éxito! Orden {orden.numero_orden} procesada.")
            return redirect('checkout_exito', orden_id=orden.id)
        except DRFValidationError as e:
            err_msg = e.detail.get('error', str(e.detail)) if isinstance(e.detail, dict) else str(e.detail)
            messages.error(request, err_msg)
            return redirect('checkout')


class CheckoutExitoWebView(LoginRequiredMixin, View):
    """
    Pantalla de confirmación y agradecimiento tras compra exitosa.
    """
    login_url = 'login'

    def get(self, request, orden_id):
        orden = get_object_or_404(
            Orden.objects.prefetch_related('items__producto'),
            id=orden_id,
            usuario=request.user
        )
        return render(request, 'ordenes/exito.html', {'orden': orden})


class MisOrdenesWebView(LoginRequiredMixin, View):
    """
    Vista web para consultar el historial de compras del cliente autenticado.
    """
    login_url = 'login'

    def get(self, request):
        if request.user.role != CustomUser.Role.CLIENTE:
            messages.info(request, "Solo los clientes disponen de historial de compras.")
            return redirect('catalogo')

        ordenes = (
            Orden.objects.filter(usuario=request.user)
            .prefetch_related('items__producto')
            .order_by('-creado_en')
        )
        return render(request, 'ordenes/mis_ordenes.html', {'ordenes': ordenes})
