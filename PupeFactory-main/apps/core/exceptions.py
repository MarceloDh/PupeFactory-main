from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from rest_framework.exceptions import NotFound, PermissionDenied, NotAuthenticated

# ==============================================================================
# MANEJADOR PERSONALIZADO DE EXCEPCIONES PARA DRF (API REST)
# ==============================================================================
# Asegura respuestas limpias y consistentes en formato JSON sin exponer
# stack traces ni detalles internos del servidor.
# ==============================================================================

def custom_exception_handler(exc, context):
    """
    Transforma excepciones estándar de DRF y Django en respuestas JSON amigables.
    """
    response = exception_handler(exc, context)

    # Manejo específico para 404 (Recurso no encontrado)
    if isinstance(exc, (Http404, NotFound)):
        return Response(
            {
                "error": "Recurso no encontrado.",
                "status": 404
            },
            status=status.HTTP_404_NOT_FOUND
        )

    # Manejo específico para permisos y autenticación
    if isinstance(exc, NotAuthenticated):
        return Response(
            {
                "error": "Autenticación requerida para acceder a este recurso.",
                "status": 401
            },
            status=status.HTTP_401_UNAUTHORIZED
        )

    if isinstance(exc, PermissionDenied):
        return Response(
            {
                "error": "No tienes permisos suficientes para realizar esta acción.",
                "status": 403
            },
            status=status.HTTP_403_FORBIDDEN
        )

    # Para otros errores gestionados por DRF
    if response is not None:
        error_msg = "Error en la solicitud."
        if isinstance(response.data, dict) and "error" in response.data:
            error_msg = response.data["error"]
        elif isinstance(response.data, dict) and "detail" in response.data:
            error_msg = str(response.data["detail"])
        elif isinstance(response.data, list) and len(response.data) > 0:
            error_msg = str(response.data[0])

        custom_data = {
            "status": response.status_code,
            "error": error_msg,
            "detalles": response.data
        }
        response.data = custom_data

    return response
