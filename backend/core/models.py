
from django.db import models


class Sede(models.Model):
    nombre = models.CharField("nombre", max_length=150)
    direccion = models.CharField("dirección", max_length=255)

    class Meta:
        verbose_name = "sede"
        verbose_name_plural = "sedes"

    def __str__(self):
        return self.nombre


class TipoRecurso(models.Model):
    nombre = models.CharField("nombre", max_length=150)

    class Meta:
        verbose_name = "tipo de recurso"
        verbose_name_plural = "tipos de recursos"

    def __str__(self):
        return self.nombre


class Area(models.Model):
    nombre = models.CharField("nombre", max_length=150)
    descripcion = models.TextField("descripción", blank=True)

    sede = models.ForeignKey(
        Sede,
        on_delete=models.PROTECT,
        related_name="areas",
    )

    class Meta:
        verbose_name = "área"
        verbose_name_plural = "áreas"

    def __str__(self):
        return self.nombre


class Departamento(models.Model):
    class Tipo(models.TextChoices):
        DEPARTAMENTO = "departamento", "Departamento"
        DIRECCION = "direccion", "Dirección"
        GRUPO = "grupo", "Grupo"

    nombre = models.CharField("nombre", max_length=150)

    tipo = models.CharField(
        "tipo",
        max_length=20,
        choices=Tipo.choices,
    )

    area = models.ForeignKey(
        Area,
        on_delete=models.PROTECT,
        related_name="departamentos",
    )

    centro_costo = models.CharField(
        "centro de costo",
        max_length=100,
        blank=True,
    )

    class Meta:
        verbose_name = "departamento"
        verbose_name_plural = "departamentos"

    def __str__(self):
        return self.nombre


class Equipo(models.Model):
    no_inventario = models.CharField(
        "número de inventario",
        max_length=100,
    )

    tipo_recurso = models.ForeignKey(
        TipoRecurso,
        on_delete=models.PROTECT,
        related_name="equipos",
    )

    marca = models.CharField(
        "marca",
        max_length=150,
        blank=True,
    )

    modelo = models.CharField(
        "modelo",
        max_length=150,
        blank=True,
    )

    no_serie = models.CharField(
        "número de serie",
        max_length=150,
        blank=True,
    )

    departamento = models.ForeignKey(
        Departamento,
        on_delete=models.PROTECT,
        related_name="equipos",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "equipo"
        verbose_name_plural = "equipos"

    def __str__(self):
        return (
            f"{self.no_inventario} - "
            f"{self.tipo_recurso.nombre}"
        )


# Registrar los modelos de solicitudes en Django.
from .models_solicitudes import (
    SolicitudBaja,
    EquipoEnSolicitud,
)

from .models_historial import HistorialSolicitud

from .models_inventario import PiezaDeposito
from .models_perfiles import PerfilInstitucional
from .models_movimientos import MovimientoInventario
from .models_recepcion import RecepcionEquipo
from .models_deposito import EquipoDeposito

from .models_deposito import MovimientoEquipoDeposito

from .models_ciclo_piezas import TipoPieza, SolicitudDespiece, PiezaRecuperada, SolicitudExtraccion, Notificacion

from .models_traslados import SolicitudTraslado
