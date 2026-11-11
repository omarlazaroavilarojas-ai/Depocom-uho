
from django.db import transaction
from rest_framework.exceptions import ValidationError

from .models_inventario import PiezaDeposito
from .models_movimientos import MovimientoInventario


@transaction.atomic
def registrar_movimiento(
    *,
    pieza_id,
    tipo,
    cantidad,
    motivo,
    usuario,
):
    try:
        pieza = PiezaDeposito.objects.select_for_update().get(
            pk=pieza_id
        )
    except PiezaDeposito.DoesNotExist:
        raise ValidationError({
            "pieza": "La pieza seleccionada no existe."
        })

    if cantidad <= 0:
        raise ValidationError({
            "cantidad": "La cantidad debe ser mayor que cero."
        })

    if tipo not in MovimientoInventario.Tipo.values:
        raise ValidationError({
            "tipo": "Tipo de movimiento inválido."
        })

    anterior = pieza.cantidad

    if tipo == MovimientoInventario.Tipo.ENTRADA:
        posterior = anterior + cantidad

    else:
        if cantidad > anterior:
            raise ValidationError({
                "cantidad": (
                    "No existen unidades suficientes. "
                    f"Disponibles: {anterior}."
                )
            })

        posterior = anterior - cantidad

    pieza.cantidad = posterior
    pieza.save(
        update_fields=[
            "cantidad",
            "fecha_actualizacion",
        ]
    )

    movimiento = MovimientoInventario.objects.create(
        pieza=pieza,
        tipo=tipo,
        cantidad=cantidad,
        existencia_anterior=anterior,
        existencia_posterior=posterior,
        motivo=motivo,
        usuario=usuario,
    )

    return movimiento


@transaction.atomic
def registrar_existencia_inicial(
    *,
    pieza,
    cantidad,
    usuario,
):
    if cantidad <= 0:
        return None

    return MovimientoInventario.objects.create(
        pieza=pieza,
        tipo=MovimientoInventario.Tipo.ENTRADA,
        cantidad=cantidad,
        existencia_anterior=0,
        existencia_posterior=cantidad,
        motivo="Registro de existencia inicial",
        usuario=usuario,
    )
