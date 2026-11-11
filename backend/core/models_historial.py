
from django.conf import settings
from django.db import models

from .models_solicitudes import SolicitudBaja


class HistorialSolicitud(models.Model):

    class Accion(models.TextChoices):
        CREACION = "creacion", "Creación"
        EDICION = "edicion", "Edición"
        REVISION = "revision", "Revisión técnica"

        PRESENTACION = (
            "presentacion",
            "Presentación",
        )

        APROBACION_AREA = (
            "aprobacion_area",
            "Aprobación del Área",
        )

        RECHAZO_AREA = (
            "rechazo_area",
            "Rechazo del Área",
        )

        APROBACION_TECNICA = (
            "aprobacion_tecnica",
            "Aprobación técnica",
        )

        REMISION_ECONOMIA = "remision_economia", "Remisión a Economía"
        INICIO_ECONOMIA = "inicio_economia", "Inicio del proceso económico"
        APROBACION_ECONOMIA = "aprobacion_economia", "Aprobación económica"

        RECEPCION_DEPOSITO = "recepcion_deposito", "Recepción en depósito"

    solicitud = models.ForeignKey(
        SolicitudBaja,
        on_delete=models.CASCADE,
        related_name="historial",
    )

    accion = models.CharField(
        "acción",
        max_length=20,
        choices=Accion.choices,
    )

    descripcion = models.TextField(
        "descripción",
    )

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="acciones_solicitudes",
    )

    fecha = models.DateTimeField(
        "fecha",
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "evento del historial"
        verbose_name_plural = "eventos del historial"
        ordering = ["-fecha", "-id"]

    def __str__(self):
        return (
            f"{self.solicitud.numero} - "
            f"{self.get_accion_display()}"
        )
