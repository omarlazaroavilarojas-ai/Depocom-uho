from django.conf import settings
from django.db import models
from .models_solicitudes import EquipoEnSolicitud


class RecepcionEquipo(models.Model):
    equipo_solicitud = models.OneToOneField(
        EquipoEnSolicitud, on_delete=models.PROTECT,
        related_name="recepcion_deposito",
    )
    recibido_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name="recepciones_deposito",
    )
    fecha_recepcion = models.DateTimeField(auto_now_add=True)
    observaciones = models.TextField(blank=True)

    class Meta:
        verbose_name = "recepción de equipo"
        verbose_name_plural = "recepciones de equipos"
        ordering = ["-fecha_recepcion", "-id"]

    def __str__(self):
        return f"Recepción {self.equipo_solicitud_id}"
