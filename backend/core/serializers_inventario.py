
from rest_framework import serializers

from .models_inventario import PiezaDeposito


class PiezaDepositoSerializer(serializers.ModelSerializer):
    estado_nombre = serializers.CharField(
        source="get_estado_display",
        read_only=True,
    )

    class Meta:
        model = PiezaDeposito

        fields = (
            "id",
            "codigo",
            "nombre",
            "descripcion",
            "cantidad",
            "estado",
            "estado_nombre",
            "ubicacion",
            "fecha_creacion",
            "fecha_actualizacion",
        )

        read_only_fields = (
            "id",
            "estado_nombre",
            "fecha_creacion",
            "fecha_actualizacion",
        )

    def validate_codigo(self, value):
        codigo = value.strip().upper()

        if not codigo:
            raise serializers.ValidationError(
                "El código es obligatorio."
            )

        existentes = PiezaDeposito.objects.filter(
            codigo__iexact=codigo
        )

        if self.instance:
            existentes = existentes.exclude(
                pk=self.instance.pk
            )

        if existentes.exists():
            raise serializers.ValidationError(
                "Ya existe una pieza con este código."
            )

        return codigo

    def validate_nombre(self, value):
        nombre = value.strip()

        if not nombre:
            raise serializers.ValidationError(
                "El nombre es obligatorio."
            )

        return nombre

    def validate_cantidad(self, value):
        if self.instance is not None:
            raise serializers.ValidationError(
                "La cantidad no puede modificarse directamente. "
                "Utiliza un movimiento de inventario."
            )

        if value < 0:
            raise serializers.ValidationError(
                "La cantidad no puede ser negativa."
            )

        return value

    def validate(self, attrs):
        if self.instance is not None:
            if "cantidad" in self.initial_data:
                raise serializers.ValidationError({
                    "cantidad": (
                        "Utiliza un movimiento de inventario "
                        "para cambiar las existencias."
                    )
                })

        return attrs
