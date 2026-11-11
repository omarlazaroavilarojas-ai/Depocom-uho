
from rest_framework.permissions import BasePermission

from .roles import (
    ADMINISTRADOR,
    JEFE_DEPARTAMENTO,
    JEFE_AREA,
    TECNICO_SOPORTE,
    JEFE_SOPORTE,
    JEFE_ECONOMIA,
    CONSULTOR,
    tiene_rol,
)


class EsSuperusuarioDesarrollo(BasePermission):
    """
    Compatibilidad temporal con las vistas existentes.

    Se conserva hasta migrar cada operación
    a los permisos institucionales definitivos.
    """

    message = (
        "Solo un superusuario autenticado puede "
        "realizar esta operación durante el desarrollo."
    )

    def has_permission(self, request, view):
        usuario = request.user

        return bool(
            usuario
            and usuario.is_authenticated
            and usuario.is_active
            and usuario.is_superuser
        )


class PermisoPorRoles(BasePermission):
    """
    Clase base para verificar roles institucionales.

    Cada vista debe indicar explícitamente
    los roles autorizados.
    """

    roles_permitidos = ()

    message = (
        "No tienes permisos para realizar esta operación."
    )

    def has_permission(self, request, view):
        return tiene_rol(
            request.user,
            *self.roles_permitidos,
        )


class EsAdministrador(PermisoPorRoles):
    roles_permitidos = (ADMINISTRADOR,)


class EsJefeDepartamento(PermisoPorRoles):
    roles_permitidos = (JEFE_DEPARTAMENTO,)


class EsJefeArea(PermisoPorRoles):
    roles_permitidos = (JEFE_AREA,)


class EsTecnicoSoporte(PermisoPorRoles):
    roles_permitidos = (TECNICO_SOPORTE,)


class EsJefeSoporte(PermisoPorRoles):
    roles_permitidos = (JEFE_SOPORTE,)


class EsJefeEconomia(PermisoPorRoles):
    roles_permitidos = (JEFE_ECONOMIA,)


class EsConsultor(PermisoPorRoles):
    roles_permitidos = (CONSULTOR,)


class PuedeCrearSolicitud(PermisoPorRoles):
    roles_permitidos = (
        ADMINISTRADOR,
        JEFE_DEPARTAMENTO,
    )


class PuedeAprobarArea(PermisoPorRoles):
    roles_permitidos = (
        ADMINISTRADOR,
        JEFE_AREA,
    )


class PuedeRealizarRevision(PermisoPorRoles):
    roles_permitidos = (
        ADMINISTRADOR,
        TECNICO_SOPORTE,
        JEFE_SOPORTE,
    )


class PuedeAprobarRevision(PermisoPorRoles):
    roles_permitidos = (
        ADMINISTRADOR,
        JEFE_SOPORTE,
    )


class PuedeAprobarEconomia(PermisoPorRoles):
    roles_permitidos = (
        ADMINISTRADOR,
        JEFE_ECONOMIA,
    )


class PuedeRegistrarPiezas(PermisoPorRoles):
    roles_permitidos = (
        ADMINISTRADOR,
        TECNICO_SOPORTE,
        JEFE_SOPORTE,
    )


class PuedeAprobarDespiece(PermisoPorRoles):
    roles_permitidos = (
        ADMINISTRADOR,
        JEFE_SOPORTE,
    )


class PuedeAprobarExtraccion(PermisoPorRoles):
    roles_permitidos = (
        ADMINISTRADOR,
        JEFE_SOPORTE,
    )
