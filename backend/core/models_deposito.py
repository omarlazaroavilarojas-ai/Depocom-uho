"""Inventario físico de equipos recibidos en depósito (distinto de piezas)."""
from django.db import models
from .models_recepcion import RecepcionEquipo


class EquipoDeposito(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = 'pendiente_clasificacion', 'Pendiente de clasificación'
        REVISION = 'revision', 'En revisión'
        DISPONIBLE = 'disponible', 'Disponible'
        NO_UTILIZABLE = 'no_utilizable', 'No utilizable'

    recepcion = models.OneToOneField(
        RecepcionEquipo, on_delete=models.PROTECT, related_name='registro_deposito'
    )
    ubicacion = models.CharField(max_length=150, blank=True)
    estado = models.CharField(max_length=30, choices=Estado.choices, default=Estado.PENDIENTE)
    observaciones = models.TextField(blank=True)
    fecha_salida = models.DateTimeField(null=True, blank=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-recepcion__fecha_recepcion', '-id']
        verbose_name = 'equipo del depósito'
        verbose_name_plural = 'equipos del depósito'

    def __str__(self):
        return f'Equipo en depósito: {self.recepcion.equipo_solicitud.equipo.no_inventario}'


class MovimientoEquipoDeposito(models.Model):
    class Tipo(models.TextChoices):
        SALIDA = 'salida', 'Salida definitiva'
        REUBICACION = 'reubicacion', 'Reubicación interna'

    equipo_deposito = models.ForeignKey(EquipoDeposito, on_delete=models.PROTECT, related_name='movimientos')
    tipo = models.CharField(max_length=20, choices=Tipo.choices)
    ubicacion_anterior = models.CharField(max_length=150, blank=True)
    ubicacion_nueva = models.CharField(max_length=150, blank=True)
    destinatario = models.CharField(max_length=200, blank=True)
    motivo = models.TextField()
    realizado_por = models.ForeignKey('auth.User', on_delete=models.PROTECT, related_name='movimientos_equipos_deposito')
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha', '-id']

