
from rest_framework import serializers

from .models import (
    Sede,
    Area,
    TipoRecurso,
    Departamento,
    Equipo,
)


class SedeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sede
        fields = (
            "id",
            "nombre",
            "direccion",
        )


class TipoRecursoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoRecurso
        fields = (
            "id",
            "nombre",
        )


class AreaSerializer(serializers.ModelSerializer):
    sede_nombre = serializers.CharField(source="sede.nombre", read_only=True)

    class Meta:
        model = Area
        fields = ("id", "nombre", "descripcion", "sede", "sede_nombre")
        read_only_fields = ("id", "sede_nombre")


class DepartamentoSerializer(serializers.ModelSerializer):
    area_nombre = serializers.CharField(
        source="area.nombre",
        read_only=True,
    )

    sede_nombre = serializers.CharField(
        source="area.sede.nombre",
        read_only=True,
    )

    class Meta:
        model = Departamento
        fields = (
            "id",
            "nombre",
            "tipo",
            "centro_costo",
            "area",
            "area_nombre",
            "sede_nombre",
        )

        read_only_fields = ("id", "area_nombre", "sede_nombre")


class EquipoSerializer(serializers.ModelSerializer):
    tipo_recurso_nombre = serializers.CharField(
        source="tipo_recurso.nombre",
        read_only=True,
    )

    departamento_nombre = serializers.CharField(
        source="departamento.nombre",
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = Equipo
        fields = (
            "id",
            "no_inventario",
            "tipo_recurso",
            "tipo_recurso_nombre",
            "marca",
            "modelo",
            "no_serie",
            "departamento",
            "departamento_nombre",
        )

        read_only_fields = fields


class EquipoCrearSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipo
        fields = (
            "id",
            "no_inventario",
            "tipo_recurso",
            "marca",
            "modelo",
            "no_serie",
            "departamento",
        )

        read_only_fields = ("id",)

    def validate_no_inventario(self, value):
        valor = value.strip()

        if not valor:
            raise serializers.ValidationError(
                "El número de inventario es obligatorio."
            )

        return valor
