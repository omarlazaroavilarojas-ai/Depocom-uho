"""Trazabilidad individual de componentes reutilizables y aprobaciones técnicas."""
from django.conf import settings
from django.db import models


class TipoPieza(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    campos_adicionales = models.JSONField(default=list, blank=True)

    def __str__(self):
        return self.nombre


class SolicitudDespiece(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = 'pendiente', 'Pendiente'
        APROBADA = 'aprobada', 'Aprobada'
        RECHAZADA = 'rechazada', 'Rechazada'
        REALIZADA = 'realizada', 'Realizada'

    equipo = models.ForeignKey('core.EquipoDeposito', on_delete=models.PROTECT, related_name='despieces')
    solicitante = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='despieces_solicitados')
    fecha_sugerida = models.DateTimeField()
    participantes = models.TextField(blank=True)
    justificacion = models.TextField()
    estado = models.CharField(max_length=15, choices=Estado.choices, default=Estado.PENDIENTE)
    fecha_confirmada = models.DateTimeField(null=True, blank=True)
    aprobado_por = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT, related_name='despieces_aprobados')
    ejecutado_por = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT, related_name='despieces_ejecutados')
    comentario_decision = models.TextField(blank=True)
    creado = models.DateTimeField(auto_now_add=True)
    ejecutado = models.DateTimeField(null=True, blank=True)


class PiezaRecuperada(models.Model):
    class Estado(models.TextChoices):
        DISPONIBLE = 'disponible', 'Disponible'
        RESERVADA = 'reservada', 'Reservada'
        INSTALADA = 'instalada', 'Instalada'
        NO_UTILIZABLE = 'no_utilizable', 'No utilizable'

    despiece = models.ForeignKey(SolicitudDespiece, on_delete=models.PROTECT, related_name='piezas')
    tipo = models.ForeignKey(TipoPieza, on_delete=models.PROTECT)
    codigo = models.CharField(max_length=70, unique=True)
    marca = models.CharField(max_length=150, blank=True)
    modelo = models.CharField(max_length=150, blank=True)
    capacidad = models.CharField(max_length=100, blank=True)
    numero_serie = models.CharField(max_length=150, blank=True)
    descripcion = models.TextField(blank=True)
    atributos = models.JSONField(default=dict, blank=True)
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.DISPONIBLE)
    ingresada = models.DateTimeField(auto_now_add=True)
    equipo_destino = models.ForeignKey('core.Equipo', on_delete=models.PROTECT, null=True, blank=True, related_name='piezas_instaladas')
    instalada = models.DateTimeField(null=True, blank=True)


class SolicitudExtraccion(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = 'pendiente', 'Pendiente'
        RECHAZADA = 'rechazada', 'Rechazada'
        RESERVADA = 'reservada', 'Reservada'
        INSTALADA = 'instalada', 'Instalada'
        CANCELADA = 'cancelada', 'Cancelada'

    pieza = models.ForeignKey(PiezaRecuperada, on_delete=models.PROTECT, related_name='solicitudes')
    equipo_destino = models.ForeignKey('core.Equipo', on_delete=models.PROTECT, related_name='extracciones_destino')
    solicitante = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='extracciones_solicitadas')
    autorizado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True, related_name='extracciones_autorizadas')
    instalado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True, related_name='extracciones_instaladas')
    estado = models.CharField(max_length=15, choices=Estado.choices, default=Estado.PENDIENTE)
    motivo = models.TextField()
    comentario = models.TextField(blank=True)
    creada = models.DateTimeField(auto_now_add=True)
    autorizada = models.DateTimeField(null=True, blank=True)
    instalada = models.DateTimeField(null=True, blank=True)


class Notificacion(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notificaciones_depocom')
    titulo = models.CharField(max_length=160)
    mensaje = models.TextField()
    creada = models.DateTimeField(auto_now_add=True)
    leida = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-creada', '-id']
