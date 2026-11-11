
from django.core.validators import MinValueValidator
from django.db import models


class PiezaDeposito(models.Model):
    class Estado(models.TextChoices):
        DISPONIBLE = "disponible", "Disponible"
        REVISION = "revision", "En revisión"
        NO_UTILIZABLE = "no_utilizable", "No utilizable"

    codigo = models.CharField(
        "código de la pieza",
        max_length=50,
        unique=True,
    )

    nombre = models.CharField(
        "nombre",
        max_length=150,
    )

    descripcion = models.TextField(
        "descripción",
        blank=True,
    )

    cantidad = models.PositiveIntegerField(
        "cantidad",
        default=0,
        validators=[MinValueValidator(0)],
    )

    estado = models.CharField(
        "estado",
        max_length=20,
        choices=Estado.choices,
        default=Estado.DISPONIBLE,
    )

    ubicacion = models.CharField(
        "ubicación en el depósito",
        max_length=150,
        blank=True,
    )

    fecha_creacion = models.DateTimeField(
        "fecha de creación",
        auto_now_add=True,
    )

    fecha_actualizacion = models.DateTimeField(
        "última actualización",
        auto_now=True,
    )

    class Meta:
        verbose_name = "pieza del depósito"
        verbose_name_plural = "piezas del depósito"
        ordering = ["nombre", "id"]

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
