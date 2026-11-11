from django.conf import settings
from django.db import models

class SolicitudTraslado(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = 'pendiente', 'Pendiente'
        APROBADA = 'aprobada', 'Aprobada'
        RECHAZADA = 'rechazada', 'Rechazada'
        EJECUTADA = 'ejecutada', 'Ejecutada'

    equipo = models.ForeignKey('core.EquipoDeposito', on_delete=models.PROTECT, related_name='solicitudes_traslado')
    departamento_destino = models.ForeignKey('core.Departamento', on_delete=models.PROTECT, related_name='traslados_recibidos')
    solicitante = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='traslados_solicitados')
    justificacion = models.TextField()
    fecha_prevista = models.DateField()
    estado = models.CharField(max_length=12, choices=Estado.choices, default=Estado.PENDIENTE)
    comentario_decision = models.TextField(blank=True)
    decidido_en = models.DateTimeField(null=True, blank=True)
    ejecutado_en = models.DateTimeField(null=True, blank=True)
    creado = models.DateTimeField(auto_now_add=True)
    decidido_por = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT, related_name='traslados_decididos')
    ejecutado_por = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT, related_name='traslados_ejecutados')

    class Meta:
        ordering = ['-creado', '-id']
