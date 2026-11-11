
from django.conf import settings
from django.db import models

from .models import Equipo


class SolicitudBaja(models.Model):

    class Estado(models.TextChoices):
        BORRADOR = "borrador", "Borrador"
        PRESENTADA = "presentada", "Presentada"

        APROBADA_AREA = (
            "aprobada_area",
            "Aprobada por Área",
        )

        RECHAZADA_AREA = (
            "rechazada_area",
            "Rechazada por Área",
        )

        EN_REVISION = (
            "en_revision",
            "En Revisión Técnica",
        )

        APROBADA_TECNICAMENTE = (
            "aprobada_tecnica",
            "Aprobada Técnicamente",
        )

        PENDIENTE_ECONOMIA = (
            "pendiente_economia",
            "Pendiente Movimiento Economía",
        )

        EN_PROCESO_ECONOMICO = (
            "proceso_economico",
            "En Proceso Económico",
        )

        APROBADA_ECONOMIA = (
            "aprobada_economia",
            "Aprobada por Economía",
        )

        RECIBIDA_DEPOSITO = (
            "recibida_deposito",
            "Recibida en Depósito",
        )

    numero = models.CharField(
        "número de solicitud",
        max_length=50,
        unique=True,
    )

    fecha_creacion = models.DateTimeField(
        "fecha de creación",
        auto_now_add=True,
    )

    solicitante = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="solicitudes_baja",
    )

    departamento = models.ForeignKey(
        "core.Departamento",
        on_delete=models.PROTECT,
        related_name="solicitudes_baja",
        null=True,
        blank=True,
    )

    observaciones = models.TextField(
        "observaciones",
        blank=True,
    )

    estado = models.CharField(
        "estado",
        max_length=20,
        choices=Estado.choices,
        default=Estado.BORRADOR,
    )

    class Meta:
        verbose_name = "solicitud de baja"
        verbose_name_plural = "solicitudes de baja"
        ordering = ["-fecha_creacion"]

    def __str__(self):
        return self.numero


class EquipoEnSolicitud(models.Model):

    solicitud = models.ForeignKey(
        SolicitudBaja,
        on_delete=models.CASCADE,
        related_name="equipos_asociados",
    )

    equipo = models.ForeignKey(
        Equipo,
        on_delete=models.PROTECT,
        related_name="solicitudes_asociadas",
    )

    observaciones = models.TextField(
        "observaciones",
        blank=True,
    )

    class Meta:
        verbose_name = "equipo en solicitud"
        verbose_name_plural = "equipos en solicitudes"

        constraints = [
            models.UniqueConstraint(
                fields=["solicitud", "equipo"],
                name="equipo_unico_por_solicitud",
            )
        ]

    def __str__(self):
        return (
            f"{self.solicitud.numero} - "
            f"{self.equipo.no_inventario}"
        )


class RevisionTecnica(models.Model):

    class Condicion(models.TextChoices):
        BUENA = "buena", "Buena"
        REGULAR = "regular", "Regular"
        MALA = "mala", "Mala"
        NO_EVALUADA = (
            "no_evaluada",
            "No evaluada",
        )

    equipo_solicitud = models.OneToOneField(
        EquipoEnSolicitud,
        on_delete=models.CASCADE,
        related_name="revision_tecnica",
    )

    condicion_fisica = models.CharField(
        "condición física",
        max_length=20,
        choices=Condicion.choices,
        default=Condicion.NO_EVALUADA,
    )

    diagnostico = models.TextField(
        "diagnóstico técnico",
        blank=True,
    )

    observaciones = models.TextField(
        "observaciones técnicas",
        blank=True,
    )

    fecha_revision = models.DateTimeField(
        "fecha de revisión",
        auto_now=True,
    )

    revisado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="revisiones_tecnicas",
    )

    class Meta:
        verbose_name = "revisión técnica"
        verbose_name_plural = "revisiones técnicas"

    def __str__(self):
        return (
            f"Revisión de "
            f"{self.equipo_solicitud.equipo.no_inventario}"
        )
