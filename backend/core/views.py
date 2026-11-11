
import json

from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST

from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import Sede, Area, TipoRecurso, Departamento, Equipo
from .permissions import EsSuperusuarioDesarrollo, EsAdministrador
from .roles import (
    ADMINISTRADOR,
    JEFE_DEPARTAMENTO,
    JEFE_AREA,
    TECNICO_SOPORTE,
    JEFE_SOPORTE,
    JEFE_ECONOMIA,
    CONSULTOR,
    obtener_roles_usuario,
    tiene_rol,
)
from .serializers import (
    SedeSerializer,
    AreaSerializer,
    TipoRecursoSerializer,
    DepartamentoSerializer,
    EquipoSerializer,
    EquipoCrearSerializer,
)


def construir_datos_sesion(usuario):
    """
    Devuelve la información de sesión y las capacidades
    institucionales previstas para la interfaz.

    Las capacidades no sustituyen los permisos de las
    vistas de la API ni las validaciones de alcance.
    """
    autenticado = bool(
        usuario.is_authenticated and usuario.is_active
    )

    if not autenticado:
        return {
            "autenticado": False,
            "usuario": None,
            "roles": [],
            "permisos": {},
            "puede_crear_equipos": False,
        }

    roles = obtener_roles_usuario(usuario)

    permisos = {
        "administrar": tiene_rol(
            usuario, ADMINISTRADOR
        ),
        "crear_solicitudes": tiene_rol(
            usuario,
            ADMINISTRADOR,
            JEFE_DEPARTAMENTO,
        ),
        "aprobar_area": tiene_rol(
            usuario,
            ADMINISTRADOR,
            JEFE_AREA,
        ),
        "revision_tecnica": tiene_rol(
            usuario,
            ADMINISTRADOR,
            TECNICO_SOPORTE,
            JEFE_SOPORTE,
        ),
        "aprobar_revision": tiene_rol(
            usuario,
            ADMINISTRADOR,
            JEFE_SOPORTE,
        ),
        "aprobar_economia": tiene_rol(
            usuario,
            ADMINISTRADOR,
            JEFE_ECONOMIA,
        ),
        "registrar_piezas": tiene_rol(
            usuario,
            ADMINISTRADOR,
            TECNICO_SOPORTE,
            JEFE_SOPORTE,
        ),
        "aprobar_despiece": tiene_rol(
            usuario,
            ADMINISTRADOR,
            JEFE_SOPORTE,
        ),
        "aprobar_extraccion": tiene_rol(
            usuario,
            ADMINISTRADOR,
            JEFE_SOPORTE,
        ),
        "consultar": bool(roles),
    }

    return {
        "autenticado": True,
        "usuario": usuario.get_username(),
        "roles": roles,
        "permisos": permisos,

        # Compatibilidad con los componentes anteriores.
        # Por ahora la API de equipos sigue exigiendo
        # superusuario para operaciones de escritura.
        "puede_crear_equipos": bool(
            usuario.is_superuser
        ),
    }


@require_GET
def estado_api(request):
    return JsonResponse({
        "proyecto": "DepoCom UHO",
        "estado": "funcionando",
        "mensaje": (
            "El backend de DepoCom UHO está activo"
        ),
    })


@require_GET
@ensure_csrf_cookie
def iniciar_csrf(request):
    return JsonResponse({
        "mensaje": "Protección CSRF preparada"
    })


@require_GET
def sesion_actual(request):
    return JsonResponse(
        construir_datos_sesion(request.user)
    )


@require_POST
@csrf_protect
def iniciar_sesion(request):
    try:
        datos = json.loads(
            request.body.decode("utf-8")
        )
    except (ValueError, UnicodeDecodeError):
        return JsonResponse(
            {"error": "JSON inválido."},
            status=400,
        )

    if not isinstance(datos, dict):
        return JsonResponse(
            {"error": "Datos inválidos."},
            status=400,
        )

    usuario_nombre = datos.get("usuario", "")
    contrasena = datos.get("contrasena", "")

    if (
        not isinstance(usuario_nombre, str)
        or not isinstance(contrasena, str)
    ):
        return JsonResponse(
            {"error": "Credenciales inválidas."},
            status=400,
        )

    usuario = authenticate(
        request,
        username=usuario_nombre,
        password=contrasena,
    )

    if usuario is None or not usuario.is_active:
        return JsonResponse(
            {"error": "Credenciales incorrectas."},
            status=401,
        )

    login(request, usuario)

    return JsonResponse(
        construir_datos_sesion(usuario)
    )


@require_POST
@csrf_protect
def cerrar_sesion(request):
    logout(request)

    return JsonResponse({
        "autenticado": False,
        "usuario": None,
        "roles": [],
        "permisos": {},
        "puede_crear_equipos": False,
        "mensaje": "Sesión cerrada.",
    })


class CatalogoPermisosMixin:
    """Lectura autenticada; escritura solo para administradores."""
    def get_permissions(self):
        if self.request.method in ("GET", "HEAD", "OPTIONS"):
            return [IsAuthenticated()]
        return [EsAdministrador()]


class SedeListView(CatalogoPermisosMixin, generics.ListCreateAPIView):
    queryset = Sede.objects.all().order_by("id")
    serializer_class = SedeSerializer


class SedeDetailView(CatalogoPermisosMixin, generics.RetrieveUpdateAPIView):
    queryset = Sede.objects.all()
    serializer_class = SedeSerializer


class AreaListView(CatalogoPermisosMixin, generics.ListCreateAPIView):
    queryset = Area.objects.select_related("sede").order_by("nombre", "id")
    serializer_class = AreaSerializer


class AreaDetailView(CatalogoPermisosMixin, generics.RetrieveUpdateAPIView):
    queryset = Area.objects.select_related("sede")
    serializer_class = AreaSerializer


class TipoRecursoListView(CatalogoPermisosMixin, generics.ListCreateAPIView):
    queryset = TipoRecurso.objects.all().order_by("id")
    serializer_class = TipoRecursoSerializer


class TipoRecursoDetailView(CatalogoPermisosMixin, generics.RetrieveUpdateAPIView):
    queryset = TipoRecurso.objects.all()
    serializer_class = TipoRecursoSerializer


class DepartamentoListView(CatalogoPermisosMixin, generics.ListCreateAPIView):
    serializer_class = DepartamentoSerializer

    def get_queryset(self):
        return Departamento.objects.select_related(
            "area", "area__sede"
        ).order_by("nombre", "id")


class DepartamentoDetailView(CatalogoPermisosMixin, generics.RetrieveUpdateAPIView):
    queryset = Departamento.objects.select_related("area", "area__sede")
    serializer_class = DepartamentoSerializer


class EquipoListView(generics.ListCreateAPIView):

    def get_serializer_class(self):
        if self.request.method == "POST":
            return EquipoCrearSerializer
        return EquipoSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [EsSuperusuarioDesarrollo()]

    def get_queryset(self):
        return Equipo.objects.select_related(
            "tipo_recurso", "departamento"
        ).order_by("id")


class EquipoDetailView(
    generics.RetrieveUpdateAPIView
):

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return EquipoCrearSerializer
        return EquipoSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [EsSuperusuarioDesarrollo()]

    def get_queryset(self):
        return Equipo.objects.select_related(
            "tipo_recurso", "departamento"
        )
