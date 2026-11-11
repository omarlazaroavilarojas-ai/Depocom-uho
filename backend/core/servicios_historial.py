
from .models_historial import HistorialSolicitud


def registrar_evento(
    solicitud,
    usuario,
    accion,
    descripcion,
):
    return HistorialSolicitud.objects.create(
        solicitud=solicitud,
        usuario=usuario,
        accion=accion,
        descripcion=descripcion,
    )

