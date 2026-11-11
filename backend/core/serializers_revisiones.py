
from rest_framework import serializers

from .models_solicitudes import RevisionTecnica


class RevisionTecnicaSerializer(serializers.ModelSerializer):
    revisor_nombre = serializers.CharField(
        source="revisado_por.username",
        read_only=True,
    )

    class Meta:
        model = RevisionTecnica
        fields = (
            "id",
            "equipo_solicitud",
            "condicion_fisica",
            "diagnostico",
            "observaciones",
            "fecha_revision",
            "revisado_por",
            "revisor_nombre",
        )

        read_only_fields = (
            "id",
            "equipo_solicitud",
            "fecha_revision",
            "revisado_por",
            "revisor_nombre",
        )


class GuardarRevisionTecnicaSerializer(serializers.ModelSerializer):
    class Meta:
        model = RevisionTecnica
        fields = (
            "condicion_fisica",
            "diagnostico",
            "observaciones",
        )

    def validate(self, attrs):
        if not attrs.get(
            "diagnostico",
            getattr(self.instance, "diagnostico", ""),
        ).strip():
            raise serializers.ValidationError({
                "diagnostico": (
                    "Debes escribir un diagnóstico técnico."
                )
            })

        return attrs
