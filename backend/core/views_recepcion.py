from drf_spectacular.utils import extend_schema, OpenApiTypes
"""Recepción física por equipo de solicitudes aprobadas económicamente."""
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .alcance import obtener_perfil, puede_consultar_solicitud
from .models_historial import HistorialSolicitud
from .models_recepcion import RecepcionEquipo
from .models_deposito import EquipoDeposito
from .models_solicitudes import EquipoEnSolicitud, SolicitudBaja
from .roles import ADMINISTRADOR, JEFE_SOPORTE, TECNICO_SOPORTE, tiene_rol
from .servicios_historial import registrar_evento


def comprobar_receptor(usuario, solicitud):
    if tiene_rol(usuario, ADMINISTRADOR):
        return
    if not tiene_rol(usuario, JEFE_SOPORTE, TECNICO_SOPORTE):
        raise PermissionDenied("Solo soporte autorizado puede recibir equipos.")
    perfil = obtener_perfil(usuario)
    if (perfil is None or perfil.sede_id is None
            or solicitud.departamento_id is None
            or solicitud.departamento.area.sede_id != perfil.sede_id):
        raise PermissionDenied("La solicitud no pertenece a tu sede.")


def resumen(solicitud):
    asociaciones = EquipoEnSolicitud.objects.filter(solicitud=solicitud).select_related("equipo").order_by("id")
    recibidos = set(RecepcionEquipo.objects.filter(equipo_solicitud__solicitud=solicitud).values_list("equipo_solicitud_id", flat=True))
    equipos = [{"equipo_solicitud_id": item.id, "equipo_id": item.equipo_id,
                "no_inventario": item.equipo.no_inventario,
                "recibido": item.id in recibidos} for item in asociaciones]
    return {"solicitud_id": solicitud.pk, "numero": solicitud.numero,
            "estado": solicitud.estado, "total": len(equipos),
            "recibidos": len(recibidos), "pendientes": len(equipos)-len(recibidos),
            "equipos": equipos}


class RecepcionSolicitudView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(operation_id="recepcionsolicitudview_get", description="RecepcionSolicitudView: GET.", responses=OpenApiTypes.ANY)
    def get(self, request, pk):
        solicitud = get_object_or_404(SolicitudBaja, pk=pk)
        if not puede_consultar_solicitud(request.user, solicitud):
            raise PermissionDenied("No tienes acceso a esta solicitud.")
        return Response(resumen(solicitud))

    @extend_schema(operation_id="recepcionsolicitudview_post", description="RecepcionSolicitudView: POST.", request=OpenApiTypes.OBJECT, responses=OpenApiTypes.ANY)
    @transaction.atomic
    def post(self, request, pk):
        # Bloquear solo la tabla principal: departamento es nullable.
        solicitud = get_object_or_404(SolicitudBaja.objects.select_for_update(), pk=pk)
        comprobar_receptor(request.user, solicitud)
        if solicitud.estado not in (
            SolicitudBaja.Estado.APROBADA_ECONOMIA,
            SolicitudBaja.Estado.RECIBIDA_DEPOSITO,
        ):
            raise ValidationError({"estado": "Se requiere aprobación económica previa."})
        if not isinstance(request.data, dict):
            raise ValidationError({"detalle": "Envía un objeto JSON."})
        equipo_id = request.data.get("equipo_solicitud_id")
        if isinstance(equipo_id, bool) or not isinstance(equipo_id, int):
            raise ValidationError({"equipo_solicitud_id": "Indica un ID entero."})
        observaciones = request.data.get("observaciones", "")
        if not isinstance(observaciones, str) or len(observaciones) > 2000:
            raise ValidationError({"observaciones": "Debe ser texto de hasta 2000 caracteres."})
        asociacion = get_object_or_404(EquipoEnSolicitud, pk=equipo_id, solicitud=solicitud)
        if RecepcionEquipo.objects.filter(equipo_solicitud=asociacion).exists():
            raise ValidationError({"equipo_solicitud_id": "Este equipo ya fue recibido."})
        recepcion = RecepcionEquipo.objects.create(
            equipo_solicitud=asociacion, recibido_por=request.user,
            observaciones=observaciones.strip(),
        )
        EquipoDeposito.objects.create(recepcion=recepcion)
        registrar_evento(
            solicitud, request.user, HistorialSolicitud.Accion.RECEPCION_DEPOSITO,
            f"Recibido equipo {asociacion.equipo.no_inventario}." +
            (f" Observaciones: {observaciones.strip()}" if observaciones.strip() else ""),
        )
        total = EquipoEnSolicitud.objects.filter(solicitud=solicitud).count()
        recibidos = RecepcionEquipo.objects.filter(equipo_solicitud__solicitud=solicitud).count()
        if total > 0 and total == recibidos:
            solicitud.estado = SolicitudBaja.Estado.RECIBIDA_DEPOSITO
            solicitud.save(update_fields=["estado"])
        return Response(resumen(solicitud), status=201)
