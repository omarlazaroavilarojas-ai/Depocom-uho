
from django.contrib.auth.models import Group


ADMINISTRADOR = "Administrador del Sistema"
JEFE_DEPARTAMENTO = "Jefe de Departamento"
JEFE_AREA = "Jefe de Área"
TECNICO_SOPORTE = "Técnico de Soporte"
JEFE_SOPORTE = "Jefe de Soporte Técnico"
JEFE_ECONOMIA = "Jefe de Economía"
CONSULTOR = "Consultor"


ROLES = (
    ADMINISTRADOR,
    JEFE_DEPARTAMENTO,
    JEFE_AREA,
    TECNICO_SOPORTE,
    JEFE_SOPORTE,
    JEFE_ECONOMIA,
    CONSULTOR,
)


def crear_grupos_roles():
    """
    Crea los grupos institucionales que aún no existan.
    No elimina grupos ni modifica sus integrantes.
    """
    for nombre in ROLES:
        Group.objects.get_or_create(name=nombre)


def obtener_roles_usuario(usuario):
    if not usuario or not usuario.is_authenticated:
        return []

    if not usuario.is_active:
        return []

    if usuario.is_superuser:
        return [ADMINISTRADOR]

    return list(
        usuario.groups.filter(
            name__in=ROLES
        ).values_list("name", flat=True)
    )


def tiene_rol(usuario, *roles_permitidos):
    if not usuario or not usuario.is_authenticated:
        return False

    if not usuario.is_active:
        return False

    if usuario.is_superuser:
        return True

    return usuario.groups.filter(
        name__in=roles_permitidos
    ).exists()


def es_administrador(usuario):
    return tiene_rol(usuario, ADMINISTRADOR)
