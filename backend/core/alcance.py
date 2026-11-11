
from .models_perfiles import PerfilInstitucional
from .roles import (
    ADMINISTRADOR,
    JEFE_DEPARTAMENTO,
    JEFE_AREA,
    JEFE_ECONOMIA,
    TECNICO_SOPORTE,
    JEFE_SOPORTE,
    tiene_rol,
)


def obtener_perfil(usuario):
    if not usuario or not usuario.is_authenticated:
        return None

    if not usuario.is_active:
        return None

    try:
        return PerfilInstitucional.objects.select_related(
            "sede", "area", "departamento"
        ).get(usuario=usuario)
    except PerfilInstitucional.DoesNotExist:
        return None


def puede_consultar_solicitud(usuario, solicitud):
    if not usuario.is_authenticated or not usuario.is_active:
        return False

    if tiene_rol(usuario, ADMINISTRADOR):
        return True

    if solicitud.departamento_id is None:
        return False

    perfil = obtener_perfil(usuario)

    if perfil is None:
        return False

    departamento = solicitud.departamento

    if tiene_rol(usuario, JEFE_DEPARTAMENTO):
        if perfil.departamento_id == solicitud.departamento_id:
            return True

    if tiene_rol(usuario, JEFE_AREA):
        if perfil.area_id == departamento.area_id:
            return True

    if tiene_rol(usuario, JEFE_ECONOMIA, TECNICO_SOPORTE, JEFE_SOPORTE):
        if (
            perfil.sede_id is not None
            and perfil.sede_id == departamento.area.sede_id
        ):
            return True

    return False


def puede_editar_solicitud(usuario, solicitud):
    if not usuario.is_authenticated or not usuario.is_active:
        return False

    if solicitud.estado != "borrador":
        return False

    if tiene_rol(usuario, ADMINISTRADOR):
        return True

    if not tiene_rol(usuario, JEFE_DEPARTAMENTO):
        return False

    perfil = obtener_perfil(usuario)

    return bool(
        perfil is not None
        and perfil.departamento_id is not None
        and perfil.departamento_id == solicitud.departamento_id
        and solicitud.solicitante_id == usuario.pk
    )
