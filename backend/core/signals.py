"""Notificaciones transaccionales de cambios de estado institucionales."""
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models_historial import HistorialSolicitud
from .models_traslados import SolicitudTraslado
from .models_ciclo_piezas import Notificacion
from .roles import JEFE_AREA, JEFE_SOPORTE, JEFE_ECONOMIA, TECNICO_SOPORTE


def emitir(usuarios, titulo, mensaje):
    ids = {u.pk for u in usuarios if u is not None and u.pk is not None and u.is_active}
    Notificacion.objects.bulk_create([
        Notificacion(usuario_id=pk, titulo=titulo[:160], mensaje=mensaje) for pk in ids
    ])


def destinatarios_por_rol(rol, sede_id=None, area_id=None):
    qs = get_user_model().objects.filter(is_active=True, groups__name=rol).distinct()
    if sede_id is not None:
        qs = qs.filter(perfil_institucional__sede_id=sede_id)
    if area_id is not None:
        qs = qs.filter(perfil_institucional__area_id=area_id)
    return qs


@receiver(post_save, sender=HistorialSolicitud, dispatch_uid='depocom_notificar_historial')
def notificar_historial(sender, instance, created, **kwargs):
    if not created:
        return
    solicitud = instance.solicitud
    depto = solicitud.departamento
    sede_id = depto.area.sede_id if depto and depto.area_id else None
    area_id = depto.area_id if depto else None
    accion = instance.accion
    roles = {
        'presentacion': (JEFE_AREA, area_id),
        'aprobada_area': (JEFE_SOPORTE, None),
        'aprobacion_area': (JEFE_SOPORTE, None),
        'aprobacion_tecnica': (JEFE_ECONOMIA, None),
        'remision_economia': (JEFE_ECONOMIA, None),
        'aprobacion_economia': (TECNICO_SOPORTE, None),
    }
    usuarios = [solicitud.solicitante]
    if accion in roles:
        rol, area = roles[accion]
        usuarios.extend(destinatarios_por_rol(rol, sede_id=sede_id, area_id=area))
    emitir(usuarios, f'Solicitud {solicitud.numero}: {instance.get_accion_display()}', instance.descripcion)


@receiver(pre_save, sender=SolicitudTraslado, dispatch_uid='depocom_estado_traslado_anterior')
def estado_traslado_anterior(sender, instance, **kwargs):
    instance._estado_previo_notificaciones = (
        sender.objects.filter(pk=instance.pk).values_list('estado', flat=True).first() if instance.pk else None
    )


@receiver(post_save, sender=SolicitudTraslado, dispatch_uid='depocom_notificar_traslado')
def notificar_traslado(sender, instance, created, **kwargs):
    if not created and instance._estado_previo_notificaciones == instance.estado:
        return
    departamento = instance.equipo.recepcion.equipo_solicitud.solicitud.departamento
    sede_id = departamento.area.sede_id if departamento and departamento.area_id else None
    usuarios = [instance.solicitante]
    if created:
        usuarios.extend(destinatarios_por_rol(JEFE_SOPORTE, sede_id=sede_id))
    elif instance.estado == 'aprobada':
        usuarios.extend(destinatarios_por_rol(TECNICO_SOPORTE, sede_id=sede_id))
    emitir(usuarios, f'Traslado #{instance.pk}: {instance.estado}',
           f'El traslado del equipo #{instance.equipo_id} está en estado {instance.estado}.')
