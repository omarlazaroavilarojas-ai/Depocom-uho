
from django.db.models import Q

from rest_framework import generics
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated

from .alcance import (
    obtener_perfil,
    puede_editar_solicitud,
)
from .models_solicitudes import SolicitudBaja
from .roles import (
    ADMINISTRADOR,
    JEFE_DEPARTAMENTO,
    JEFE_AREA,
    JEFE_ECONOMIA,
    TECNICO_SOPORTE,
    JEFE_SOPORTE,
    tiene_rol,
)
from .serializers_solicitudes import (
    SolicitudBajaSerializer,
    CrearSolicitudBajaSerializer,
    EditarSolicitudBajaSerializer,
)


def solicitudes_visibles(usuario):
    queryset = SolicitudBaja.objects.select_related(
        "solicitante",
        "departamento",
        "departamento__area",
        "departamento__area__sede",
    ).prefetch_related(
        "equipos_asociados__equipo",
        "equipos_asociados__revision_tecnica__revisado_por",
    )

    if not usuario.is_authenticated or not usuario.is_active:
        return queryset.none()

    if tiene_rol(usuario, ADMINISTRADOR):
        return queryset

    perfil = obtener_perfil(usuario)

    if perfil is None:
        return queryset.none()

    filtros = Q(pk__in=[])

    if (
        tiene_rol(usuario, JEFE_DEPARTAMENTO)
        and perfil.departamento_id is not None
    ):
        filtros |= Q(
            departamento_id=perfil.departamento_id
        )

    if (
        tiene_rol(usuario, JEFE_AREA)
        and perfil.area_id is not None
    ):
        filtros |= Q(
            departamento__area_id=perfil.area_id
        )

    if (
        tiene_rol(usuario, JEFE_ECONOMIA, TECNICO_SOPORTE, JEFE_SOPORTE)
        and perfil.sede_id is not None
    ):
        filtros |= Q(
            departamento__area__sede_id=perfil.sede_id
        )

    return queryset.filter(filtros).distinct()


class SolicitudBajaListCreateView(
    generics.ListCreateAPIView
):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return solicitudes_visibles(
            self.request.user
        ).order_by("-fecha_creacion", "-id")

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CrearSolicitudBajaSerializer

        return SolicitudBajaSerializer

    def perform_create(self, serializer):
        usuario = self.request.user

        es_admin = tiene_rol(
            usuario, ADMINISTRADOR
        )

        es_jefe = tiene_rol(
            usuario, JEFE_DEPARTAMENTO
        )

        if not (es_admin or es_jefe):
            raise PermissionDenied(
                "No tienes permiso para crear solicitudes."
            )

        equipos = serializer.validated_data["equipos"]

        departamentos = {
            equipo.departamento_id
            for equipo in equipos
        }

        if len(departamentos) != 1:
            raise ValidationError({
                "equipos": (
                    "Todos los equipos deben pertenecer "
                    "al mismo departamento."
                )
            })

        departamento_id = next(iter(departamentos))

        if departamento_id is None:
            raise ValidationError({
                "equipos": (
                    "Los equipos deben tener un "
                    "departamento asignado."
                )
            })

        if not es_admin:
            perfil = obtener_perfil(usuario)

            if (
                perfil is None
                or perfil.departamento_id != departamento_id
            ):
                raise PermissionDenied(
                    "Solo puedes crear solicitudes "
                    "de tu departamento."
                )

        serializer.save(
            departamento_id=departamento_id
        )


class SolicitudBajaDetailView(
    generics.RetrieveUpdateAPIView
):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return solicitudes_visibles(
            self.request.user
        )

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return EditarSolicitudBajaSerializer

        return SolicitudBajaSerializer

    def perform_update(self, serializer):
        solicitud = self.get_object()

        if not puede_editar_solicitud(
            self.request.user,
            solicitud,
        ):
            raise PermissionDenied(
                "No tienes permiso para editar "
                "esta solicitud."
            )

        equipos = serializer.validated_data.get(
            "equipos"
        )

        if equipos is not None:
            if solicitud.departamento_id is None:
                raise ValidationError({
                    "equipos": (
                        "Primero debe asignarse un "
                        "departamento a la solicitud."
                    )
                })

            for equipo in equipos:
                if (
                    equipo.departamento_id
                    != solicitud.departamento_id
                ):
                    raise ValidationError({
                        "equipos": (
                            "No puedes agregar equipos "
                            "de otro departamento."
                        )
                    })

        serializer.save()
