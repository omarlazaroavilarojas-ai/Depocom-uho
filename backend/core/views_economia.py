from drf_spectacular.utils import extend_schema, OpenApiTypes
"""Transiciones económicas de solicitudes de baja. Todas son atómicas y auditadas."""
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .alcance import obtener_perfil
from .models_historial import HistorialSolicitud
from .models_solicitudes import SolicitudBaja
from .roles import ADMINISTRADOR, JEFE_SOPORTE, JEFE_ECONOMIA, tiene_rol
from .servicios_historial import registrar_evento


def obtener_solicitud_para_accion(usuario, pk, rol):
    # No combinar select_related sobre departamento nullable con FOR UPDATE.
    solicitud = get_object_or_404(
        SolicitudBaja.objects.select_for_update(), pk=pk
    )
    if tiene_rol(usuario, ADMINISTRADOR):
        return solicitud
    if not tiene_rol(usuario, rol):
        raise PermissionDenied("No tienes el rol requerido para esta operación.")
    perfil = obtener_perfil(usuario)
    if (
        perfil is None or perfil.sede_id is None
        or solicitud.departamento_id is None
        or solicitud.departamento.area.sede_id != perfil.sede_id
    ):
        raise PermissionDenied("La solicitud no pertenece a tu sede.")
    return solicitud


def leer_comentario(request):
    if not isinstance(request.data, dict):
        raise ValidationError({"detalle": "Envía un objeto JSON."})
    comentario = request.data.get("comentario", "")
    if not isinstance(comentario, str):
        raise ValidationError({"comentario": "El comentario debe ser texto."})
    comentario = comentario.strip()
    if len(comentario) > 2000:
        raise ValidationError({"comentario": "Máximo 2000 caracteres."})
    return comentario


def resultado(solicitud, mensaje):
    return Response({
        "id": solicitud.pk, "numero": solicitud.numero,
        "estado": solicitud.estado, "mensaje": mensaje,
    })


class RemitirEconomiaView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(operation_id="remitireconomiaview_post", description="RemitirEconomiaView: POST.", request=OpenApiTypes.OBJECT, responses=OpenApiTypes.ANY)
    @transaction.atomic
    def post(self, request, pk):
        solicitud = obtener_solicitud_para_accion(request.user, pk, JEFE_SOPORTE)
        if solicitud.estado != SolicitudBaja.Estado.APROBADA_TECNICAMENTE:
            raise ValidationError({"estado": "Se requiere aprobación técnica previa."})
        comentario = leer_comentario(request)
        solicitud.estado = SolicitudBaja.Estado.PENDIENTE_ECONOMIA
        solicitud.save(update_fields=["estado"])
        registrar_evento(
            solicitud, request.user, HistorialSolicitud.Accion.REMISION_ECONOMIA,
            "La solicitud se remitió a Economía." +
            (f" Comentario: {comentario}" if comentario else ""),
        )
        return resultado(solicitud, "Solicitud remitida a Economía.")


class IniciarProcesoEconomicoView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(operation_id="iniciarprocesoeconomicoview_post", description="IniciarProcesoEconomicoView: POST.", request=OpenApiTypes.OBJECT, responses=OpenApiTypes.ANY)
    @transaction.atomic
    def post(self, request, pk):
        solicitud = obtener_solicitud_para_accion(request.user, pk, JEFE_ECONOMIA)
        if solicitud.estado != SolicitudBaja.Estado.PENDIENTE_ECONOMIA:
            raise ValidationError({"estado": "La solicitud debe estar pendiente de Economía."})
        comentario = leer_comentario(request)
        solicitud.estado = SolicitudBaja.Estado.EN_PROCESO_ECONOMICO
        solicitud.save(update_fields=["estado"])
        registrar_evento(
            solicitud, request.user, HistorialSolicitud.Accion.INICIO_ECONOMIA,
            "Se inició la tramitación económica." +
            (f" Comentario: {comentario}" if comentario else ""),
        )
        return resultado(solicitud, "Proceso económico iniciado.")


class AprobarEconomiaView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(operation_id="aprobareconomiaview_post", description="AprobarEconomiaView: POST.", request=OpenApiTypes.OBJECT, responses=OpenApiTypes.ANY)
    @transaction.atomic
    def post(self, request, pk):
        solicitud = obtener_solicitud_para_accion(request.user, pk, JEFE_ECONOMIA)
        if solicitud.estado != SolicitudBaja.Estado.EN_PROCESO_ECONOMICO:
            raise ValidationError({"estado": "La solicitud no está en proceso económico."})
        comentario = leer_comentario(request)
        solicitud.estado = SolicitudBaja.Estado.APROBADA_ECONOMIA
        solicitud.save(update_fields=["estado"])
        registrar_evento(
            solicitud, request.user, HistorialSolicitud.Accion.APROBACION_ECONOMIA,
            "El jefe de Economía aprobó la solicitud." +
            (f" Comentario: {comentario}" if comentario else ""),
        )
        return resultado(solicitud, "Solicitud aprobada por Economía.")
