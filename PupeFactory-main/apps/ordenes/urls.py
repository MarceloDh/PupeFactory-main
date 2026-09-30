from django.urls import path
from apps.ordenes.views import (
    CheckoutAPIView,
    MisOrdenesAPIView,
    MiOrdenDetalleAPIView,
    OrdenEstadoAPIView,
    OrdenListAdminAPIView,
    CheckoutWebView,
    CheckoutExitoWebView,
    MisOrdenesWebView,
)

urlpatterns = [
    # =========================================================================
    # ENDPOINTS DE LA API REST (JSON / JWT BEARER)
    # =========================================================================
    # Checkout del cliente (crea orden y descuenta stock atómicamente)
    path('api/ordenes/checkout/', CheckoutAPIView.as_view(), name='api_checkout'),

    # Historial de compras del cliente autenticado
    path('api/mis-ordenes/', MisOrdenesAPIView.as_view(), name='api_mis_ordenes'),

    # Detalle de una compra del cliente autenticado (anti-IDOR)
    path('api/mis-ordenes/<int:pk>/', MiOrdenDetalleAPIView.as_view(), name='api_mi_orden_detalle'),

    # Cambio administrativo de estado de orden (manejo de stock al cancelar)
    path('api/ordenes/<int:pk>/estado/', OrdenEstadoAPIView.as_view(), name='api_orden_estado'),

    # Listado global de órdenes para administradores
    path('api/ordenes/', OrdenListAdminAPIView.as_view(), name='api_ordenes_admin_list'),

    # =========================================================================
    # VISTAS WEB TRADICIONALES (HTML / DJANGO SESSIONS)
    # =========================================================================
    # Pantalla de revisión y confirmación de checkout
    path('checkout/', CheckoutWebView.as_view(), name='checkout'),

    # Pantalla de confirmación tras compra exitosa
    path('checkout/exito/<int:orden_id>/', CheckoutExitoWebView.as_view(), name='checkout_exito'),

    # Historial de compras web para el cliente logueado
    path('mis-ordenes/', MisOrdenesWebView.as_view(), name='mis_ordenes'),
]
