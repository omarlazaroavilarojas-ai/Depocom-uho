from drf_spectacular.utils import extend_schema, OpenApiTypes

from django.db import transaction
from django.shortcuts import get_object_or_404

from rest_framework import generics
from rest_framework.exceptions import (
    PermissionDenied,
    ValidationError,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .alcance import obtener_perfil
from .models_solicitudes import (
    EquipoEnSolicitud,
    RevisionTecnica,
    SolicitudBaja,
)
from .models_historial import HistorialSolicitud
from .servicios_historial import registrar_evento
from .roles import (
    ADMINISTRADOR,
    TECNICO_SOPORTE,
    JEFE_SOPORTE,
    tiene_rol,
)
from .serializers_revisiones import (
    RevisionTecnicaSerializer,
    GuardarRevisionTecnicaSerializer,
)


def comprobar_acceso_tecnico(usuario, solicitud, aprobar=False):
    if tiene_rol(usuario, ADMINISTRADOR):
        return

    rol_requerido = (
        JEFE_SOPORTE if aprobar else TECNICO_SOPORTE
    )

    if not tiene_rol(usuario, rol_requerido):
        raise PermissionDenied(
            "No tienes el rol necesario para esta operación."
        )

    perfil = obtener_perfil(usuario)

    if (
        perfil is None
        or perfil.sede_id is None
        or solicitud.departamento_id is None
        or solicitud.departamento.area.sede_id
        != perfil.sede_id
    ):
        raise PermissionDenied(
            "La solicitud no pertenece a tu sede."
        )


def obtener_solicitud_tecnica(usuario, pk, aprobar=False):
    solicitud = get_object_or_404(
        # Bloquear solo la fila de la solicitud. La relación departamento
        # es opcional y PostgreSQL no admite FOR UPDATE sobre el lado
        # nullable de un LEFT OUTER JOIN.
        SolicitudBaja.objects.select_for_update(),
        pk=pk,
    )

    comprobar_acceso_tecnico(
        usuario, solicitud, aprobar=aprobar
    )
    return solicitud


class RevisionTecnicaDetailView(generics.RetrieveAPIView):
    serializer_class = RevisionTecnicaSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        revision = get_object_or_404(
            RevisionTecnica.objects.select_related(
                "equipo_solicitud__solicitud__departamento__area",
                "revisado_por",
            ),
            equipo_solicitud_id=self.kwargs[
                "equipo_solicitud_id"
            ],
        )

        solicitud = revision.equipo_solicitud.solicitud

        if not (
            tiene_rol(self.request.user, ADMINISTRADOR)
            or tiene_rol(self.request.user, TECNICO_SOPORTE)
            or tiene_rol(self.request.user, JEFE_SOPORTE)
        ):
            raise PermissionDenied(
                "No tienes acceso a esta revisión."
            )

        if not tiene_rol(self.request.user, ADMINISTRADOR):
            perfil = obtener_perfil(self.request.user)

            if (
                perfil is None
                or perfil.sede_id is None
                or solicitud.departamento_id is None
                or solicitud.departamento.area.sede_id
                != perfil.sede_id
            ):
                raise PermissionDenied(
                    "No puedes consultar esta revisión."
                )

        return revision


class IniciarRevisionTecnicaView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(operation_id="iniciarrevisiontecnicaview_post", description="IniciarRevisionTecnicaView: POST.", request=OpenApiTypes.OBJECT, responses=OpenApiTypes.ANY)
    @transaction.atomic
    def post(self, request, pk):
        solicitud = obtener_solicitud_tecnica(
            request.user, pk
        )

        if (
            solicitud.estado
            != SolicitudBaja.Estado.APROBADA_AREA
        ):
            raise ValidationError({
                "estado": (
                    "La solicitud debe estar aprobada "
                    "por el jefe de área."
                )
            })

        if not solicitud.equipos_asociados.exists():
            raise ValidationError({
                "equipos": (
                    "La solicitud no tiene equipos asociados."
                )
            })

        solicitud.estado = SolicitudBaja.Estado.EN_REVISION
        solicitud.save(update_fields=["estado"])

        registrar_evento(
            solicitud=solicitud,
            usuario=request.user,
            accion=HistorialSolicitud.Accion.REVISION,
            descripcion=(
                "Se inició la revisión técnica "
                "de la solicitud."
            ),
        )

        return Response({
            "id": solicitud.id,
            "numero": solicitud.numero,
            "estado": solicitud.estado,
            "mensaje": "Revisión técnica iniciada.",
        })


class GuardarRevisionTecnicaView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(operation_id="guardarrevisiontecnicaview_put", description="GuardarRevisionTecnicaView: PUT.", request=OpenApiTypes.OBJECT, responses=OpenApiTypes.ANY)
    @transaction.atomic
    def put(self, request, equipo_solicitud_id):
        asociacion = get_object_or_404(
            EquipoEnSolicitud.objects.select_related(
                "solicitud__departamento__area",
                "equipo",
            ),
            pk=equipo_solicitud_id,
        )

        solicitud = obtener_solicitud_tecnica(
            request.user,
            asociacion.solicitud_id,
        )

        if solicitud.estado != SolicitudBaja.Estado.EN_REVISION:
            raise ValidationError({
                "estado": (
                    "Solo puedes registrar diagnósticos "
                    "durante la revisión técnica."
                )
            })

        revision = RevisionTecnica.objects.filter(
            equipo_solicitud=asociacion
        ).first()

        es_nueva = revision is None

        serializer = GuardarRevisionTecnicaSerializer(
            revision,
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)

        if es_nueva:
            revision = serializer.save(
                equipo_solicitud=asociacion,
                revisado_por=request.user,
            )
        else:
            revision = serializer.save(
                revisado_por=request.user,
            )

        registrar_evento(
            solicitud=solicitud,
            usuario=request.user,
            accion=HistorialSolicitud.Accion.REVISION,
            descripcion=(
                "Se registró la revisión técnica "
                if es_nueva
                else "Se actualizó la revisión técnica "
            ) + (
                f"del equipo "
                f"{asociacion.equipo.no_inventario}."
            ),
        )

        return Response(
            RevisionTecnicaSerializer(revision).data
        )


class AprobarRevisionTecnicaView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(operation_id="aprobarrevisiontecnicaview_post", description="AprobarRevisionTecnicaView: POST.", request=OpenApiTypes.OBJECT, responses=OpenApiTypes.ANY)
    @transaction.atomic
    def post(self, request, pk):
        solicitud = obtener_solicitud_tecnica(
            request.user, pk, aprobar=True
        )

        if solicitud.estado != SolicitudBaja.Estado.EN_REVISION:
            raise ValidationError({
                "estado": (
                    "La solicitud no está en revisión técnica."
                )
            })

        equipos = list(
            solicitud.equipos_asociados.all()
        )

        if not equipos:
            raise ValidationError({
                "equipos": "No hay equipos para evaluar."
            })

        revisiones = RevisionTecnica.objects.filter(
            equipo_solicitud__solicitud=solicitud
        )

        revisiones_validas = {
            revision.equipo_solicitud_id
            for revision in revisiones
            if (
                revision.condicion_fisica
                != RevisionTecnica.Condicion.NO_EVALUADA
                and revision.diagnostico.strip()
            )
        }

        pendientes = [
            equipo.id
            for equipo in equipos
            if equipo.id not in revisiones_validas
        ]

        if pendientes:
            raise ValidationError({
                "equipos_pendientes": pendientes,
                "detalle": (
                    "Todos los equipos deben tener "
                    "una condición física evaluada "
                    "y un diagnóstico técnico."
                ),
            })

        solicitud.estado = (
            SolicitudBaja.Estado.APROBADA_TECNICAMENTE
        )
        solicitud.save(update_fields=["estado"])

        registrar_evento(
            solicitud=solicitud,
            usuario=request.user,
            accion=HistorialSolicitud.Accion.APROBACION_TECNICA,
            descripcion=(
                "El jefe de soporte técnico aprobó "
                "las revisiones de todos los equipos."
            ),
        )

        return Response({
            "id": solicitud.id,
            "numero": solicitud.numero,
            "estado": solicitud.estado,
            "mensaje": (
                "Revisión técnica aprobada correctamente."
            ),
        })
