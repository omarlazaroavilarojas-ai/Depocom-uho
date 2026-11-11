
from django.conf import settings
from django.db import models

from .models_inventario import PiezaDeposito


class MovimientoInventario(models.Model):

    class Tipo(models.TextChoices):
        ENTRADA = "entrada", "Entrada"
        SALIDA = "salida", "Salida"

    pieza = models.ForeignKey(
        PiezaDeposito,
        on_delete=models.PROTECT,
        related_name="movimientos",
    )

    tipo = models.CharField(
        max_length=10,
        choices=Tipo.choices,
    )

    cantidad = models.PositiveIntegerField()

    existencia_anterior = models.PositiveIntegerField()

    existencia_posterior = models.PositiveIntegerField()

    motivo = models.TextField(blank=True)

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="movimientos_inventario",
    )

    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "movimiento de inventario"
        verbose_name_plural = "movimientos de inventario"
        ordering = ["-fecha", "-id"]

    def __str__(self):
        return (
            f"{self.get_tipo_display()} - "
            f"{self.pieza} - {self.cantidad}"
        )
