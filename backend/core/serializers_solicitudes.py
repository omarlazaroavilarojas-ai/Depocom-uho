
from django.db import transaction
from rest_framework import serializers

from .models import Equipo
from .models_solicitudes import (
    SolicitudBaja,
    EquipoEnSolicitud,
)
from .models_historial import HistorialSolicitud
from .servicios_historial import registrar_evento
from .serializers_revisiones import RevisionTecnicaSerializer


class EquipoEnSolicitudSerializer(serializers.ModelSerializer):
    no_inventario = serializers.CharField(
        source="equipo.no_inventario",
        read_only=True,
    )

    revision_tecnica = RevisionTecnicaSerializer(
        read_only=True,
    )

    class Meta:
        model = EquipoEnSolicitud
        fields = (
            "id",
            "equipo",
            "no_inventario",
            "observaciones",
            "revision_tecnica",
        )


class SolicitudBajaSerializer(serializers.ModelSerializer):
    departamento_nombre = serializers.CharField(
        source="departamento.nombre",
        read_only=True,
        allow_null=True,
    )

    equipos_asociados = EquipoEnSolicitudSerializer(
        many=True,
        read_only=True,
    )

    solicitante_nombre = serializers.CharField(
        source="solicitante.username",
        read_only=True,
    )

    class Meta:
        model = SolicitudBaja
        fields = (
            "id",
            "numero",
            "fecha_creacion",
            "solicitante",
            "solicitante_nombre",
            "observaciones",
            "estado",
            "equipos_asociados",
            "departamento",
            "departamento_nombre",
        )

        read_only_fields = (
            "id",
            "fecha_creacion",
            "solicitante",
            "estado",
            "departamento",
        )


class HistorialSolicitudSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(
        source="usuario.username",
        read_only=True,
    )

    accion_nombre = serializers.CharField(
        source="get_accion_display",
        read_only=True,
    )

    class Meta:
        model = HistorialSolicitud
        fields = (
            "id",
            "accion",
            "accion_nombre",
            "descripcion",
            "usuario",
            "usuario_nombre",
            "fecha",
        )

        read_only_fields = fields


def validar_equipos(equipos):
    if not equipos:
        raise serializers.ValidationError(
            "Debes seleccionar al menos un equipo."
        )

    ids = [equipo.id for equipo in equipos]

    if len(ids) != len(set(ids)):
        raise serializers.ValidationError(
            "No puedes repetir un equipo en la solicitud."
        )

    return equipos


class ValidacionSolicitudMixin:
    def validate_numero(self, valor):
        numero = valor.strip()

        if not numero:
            raise serializers.ValidationError(
                "El número de solicitud es obligatorio."
            )

        existentes = SolicitudBaja.objects.filter(
            numero__iexact=numero
        )

        if self.instance is not None:
            existentes = existentes.exclude(
                pk=self.instance.pk
            )

        if existentes.exists():
            raise serializers.ValidationError(
                "Ya existe una solicitud con ese número."
            )

        return numero

    def validate_equipos(self, equipos):
        return validar_equipos(equipos)


class CrearSolicitudBajaSerializer(
    ValidacionSolicitudMixin,
    serializers.ModelSerializer,
):
    equipos = serializers.PrimaryKeyRelatedField(
        queryset=Equipo.objects.all(),
        many=True,
        write_only=True,
    )

    class Meta:
        model = SolicitudBaja
        fields = (
            "id",
            "numero",
            "observaciones",
            "equipos",
        )

        read_only_fields = ("id",)

    @transaction.atomic
    def create(self, validated_data):
        equipos = validated_data.pop("equipos")

        solicitud = SolicitudBaja.objects.create(
            solicitante=self.context["request"].user,
            **validated_data,
        )

        EquipoEnSolicitud.objects.bulk_create([
            EquipoEnSolicitud(
                solicitud=solicitud,
                equipo=equipo,
            )
            for equipo in equipos
        ])

        registrar_evento(
            solicitud=solicitud,
            usuario=self.context["request"].user,
            accion=HistorialSolicitud.Accion.CREACION,
            descripcion=(
                f"Se creó la solicitud {solicitud.numero} "
                f"con {len(equipos)} equipo(s)."
            ),
        )

        return solicitud


class EditarSolicitudBajaSerializer(
    ValidacionSolicitudMixin,
    serializers.ModelSerializer,
):
    equipos = serializers.PrimaryKeyRelatedField(
        queryset=Equipo.objects.all(),
        many=True,
        write_only=True,
        required=False,
    )

    class Meta:
        model = SolicitudBaja
        fields = (
            "id",
            "numero",
            "observaciones",
            "equipos",
        )

        read_only_fields = ("id",)

    def validate(self, attrs):
        if self.instance.estado != SolicitudBaja.Estado.BORRADOR:
            raise serializers.ValidationError({
                "estado": (
                    "Solo se pueden editar solicitudes "
                    "que estén en borrador."
                )
            })

        return attrs

    @transaction.atomic
    def update(self, instance, validated_data):
        equipos = validated_data.pop("equipos", None)

        solicitud = SolicitudBaja.objects.select_for_update().get(
            pk=instance.pk
        )

        if solicitud.estado != SolicitudBaja.Estado.BORRADOR:
            raise serializers.ValidationError({
                "estado": "La solicitud ya no está en borrador."
            })

        for campo, valor in validated_data.items():
            setattr(solicitud, campo, valor)

        solicitud.save()

        if equipos is not None:
            ids_nuevos = {equipo.id for equipo in equipos}

            solicitud.equipos_asociados.exclude(
                equipo_id__in=ids_nuevos
            ).delete()

            ids_existentes = set(
                solicitud.equipos_asociados.values_list(
                    "equipo_id",
                    flat=True,
                )
            )

            EquipoEnSolicitud.objects.bulk_create([
                EquipoEnSolicitud(
                    solicitud=solicitud,
                    equipo=equipo,
                )
                for equipo in equipos
                if equipo.id not in ids_existentes
            ])

        registrar_evento(
            solicitud=solicitud,
            usuario=self.context["request"].user,
            accion=HistorialSolicitud.Accion.EDICION,
            descripcion=(
                "Se actualizaron los datos de la solicitud."
            ),
        )

        return solicitud
