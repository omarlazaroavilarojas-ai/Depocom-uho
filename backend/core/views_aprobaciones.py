from drf_spectacular.utils import extend_schema, OpenApiTypes

from django.db import transaction
from django.shortcuts import get_object_or_404

from rest_framework.exceptions import (
    PermissionDenied,
    ValidationError,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .alcance import (
    obtener_perfil,
    puede_editar_solicitud,
)
from .models_solicitudes import SolicitudBaja
from .models_historial import HistorialSolicitud
from .roles import (
    ADMINISTRADOR,
    JEFE_AREA,
    tiene_rol,
)
from .servicios_historial import registrar_evento
from .views_solicitudes import solicitudes_visibles


def obtener_solicitud_bloqueada(usuario, pk):
    return get_object_or_404(
        solicitudes_visibles(usuario).select_for_update(
            of=("self",)
        ),
        pk=pk,
    )


class PresentarSolicitudView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(operation_id="presentarsolicitudview_post", description="PresentarSolicitudView: POST.", request=OpenApiTypes.OBJECT, responses=OpenApiTypes.ANY)
    @transaction.atomic
    def post(self, request, pk):
        solicitud = obtener_solicitud_bloqueada(
            request.user, pk
        )

        if not puede_editar_solicitud(
            request.user, solicitud
        ):
            raise PermissionDenied(
                "No puedes presentar esta solicitud."
            )

        if not solicitud.equipos_asociados.exists():
            raise ValidationError({
                "equipos": (
                    "La solicitud debe contener "
                    "al menos un equipo."
                )
            })

        solicitud.estado = (
            SolicitudBaja.Estado.PRESENTADA
        )
        solicitud.save(update_fields=["estado"])

        registrar_evento(
            solicitud=solicitud,
            usuario=request.user,
            accion=HistorialSolicitud.Accion.PRESENTACION,
            descripcion=(
                "La solicitud fue presentada "
                "para aprobación del jefe de área."
            ),
        )

        return Response({
            "id": solicitud.id,
            "numero": solicitud.numero,
            "estado": solicitud.estado,
            "mensaje": "Solicitud presentada correctamente.",
        })


class DecisionAreaView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(operation_id="decisionareaview_post", description="DecisionAreaView: POST.", request=OpenApiTypes.OBJECT, responses=OpenApiTypes.ANY)
    @transaction.atomic
    def post(self, request, pk):
        solicitud = obtener_solicitud_bloqueada(
            request.user, pk
        )

        es_admin = tiene_rol(
            request.user, ADMINISTRADOR
        )

        if not es_admin:
            if not tiene_rol(request.user, JEFE_AREA):
                raise PermissionDenied(
                    "Solo el jefe de área puede "
                    "aprobar o rechazar solicitudes."
                )

            perfil = obtener_perfil(request.user)

            if (
                perfil is None
                or perfil.area_id is None
                or solicitud.departamento_id is None
                or solicitud.departamento.area_id
                != perfil.area_id
            ):
                raise PermissionDenied(
                    "La solicitud no pertenece "
                    "a tu área."
                )

        if (
            solicitud.estado
            != SolicitudBaja.Estado.PRESENTADA
        ):
            raise ValidationError({
                "estado": (
                    "Solo pueden aprobarse o rechazarse "
                    "solicitudes presentadas."
                )
            })

        if not isinstance(request.data, dict):
            raise ValidationError({
                "detalle": "Debes enviar un objeto JSON."
            })

        decision = request.data.get("decision")
        comentario = request.data.get("comentario", "")

        if not isinstance(comentario, str):
            raise ValidationError({
                "comentario": "El comentario debe ser texto."
            })

        comentario = comentario.strip()

        if decision not in ("aprobar", "rechazar"):
            raise ValidationError({
                "decision": (
                    "La decisión debe ser "
                    "'aprobar' o 'rechazar'."
                )
            })

        if decision == "rechazar" and not comentario:
            raise ValidationError({
                "comentario": (
                    "Debes explicar por qué "
                    "rechazas la solicitud."
                )
            })

        if decision == "aprobar":
            solicitud.estado = (
                SolicitudBaja.Estado.APROBADA_AREA
            )
            accion = (
                HistorialSolicitud.Accion.APROBACION_AREA
            )
            descripcion = (
                "El jefe de área aprobó la solicitud."
            )

        else:
            solicitud.estado = (
                SolicitudBaja.Estado.RECHAZADA_AREA
            )
            accion = (
                HistorialSolicitud.Accion.RECHAZO_AREA
            )
            descripcion = (
                "El jefe de área rechazó la solicitud. "
                f"Motivo: {comentario}"
            )

        if decision == "aprobar" and comentario:
            descripcion += f" Comentario: {comentario}"

        solicitud.save(update_fields=["estado"])

        registrar_evento(
            solicitud=solicitud,
            usuario=request.user,
            accion=accion,
            descripcion=descripcion,
        )

        return Response({
            "id": solicitud.id,
            "numero": solicitud.numero,
            "estado": solicitud.estado,
            "mensaje": (
                "Decisión registrada correctamente."
            ),
        })
