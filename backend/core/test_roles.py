
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase

from .roles import (
    ROLES,
    ADMINISTRADOR,
    JEFE_DEPARTAMENTO,
    JEFE_AREA,
    crear_grupos_roles,
    obtener_roles_usuario,
    tiene_rol,
)
from .views import construir_datos_sesion


class RolesTests(TestCase):

    def setUp(self):
        User = get_user_model()

        self.admin = User.objects.create_superuser(
            username="admin_roles",
            email="adminroles@example.com",
            password="ClavePrueba123!",
        )

        self.usuario = User.objects.create_user(
            username="usuario_roles",
            password="ClavePrueba123!",
        )

        crear_grupos_roles()

    def test_creacion_de_siete_roles(self):
        for nombre in ROLES:
            self.assertTrue(
                Group.objects.filter(name=nombre).exists()
            )

    def test_creacion_de_roles_es_idempotente(self):
        crear_grupos_roles()
        crear_grupos_roles()

        self.assertEqual(
            Group.objects.filter(
                name__in=ROLES
            ).count(),
            7,
        )

    def test_superusuario_es_administrador(self):
        self.assertTrue(
            tiene_rol(self.admin, ADMINISTRADOR)
        )

    def test_usuario_sin_rol_no_es_administrador(self):
        self.assertFalse(
            tiene_rol(self.usuario, ADMINISTRADOR)
        )

    def test_usuario_con_rol_departamento(self):
        grupo = Group.objects.get(
            name=JEFE_DEPARTAMENTO
        )

        self.usuario.groups.add(grupo)

        self.assertTrue(
            tiene_rol(
                self.usuario,
                JEFE_DEPARTAMENTO,
            )
        )

        self.assertFalse(
            tiene_rol(self.usuario, JEFE_AREA)
        )

    def test_obtener_roles_usuario(self):
        grupo = Group.objects.get(
            name=JEFE_DEPARTAMENTO
        )

        self.usuario.groups.add(grupo)

        self.assertIn(
            JEFE_DEPARTAMENTO,
            obtener_roles_usuario(self.usuario),
        )

    def test_sesion_superusuario(self):
        datos = construir_datos_sesion(
            self.admin
        )

        self.assertTrue(datos["autenticado"])
        self.assertTrue(
            datos["permisos"]["administrar"]
        )
        self.assertTrue(
            datos["puede_crear_equipos"]
        )

    def test_sesion_usuario_normal(self):
        datos = construir_datos_sesion(
            self.usuario
        )

        self.assertTrue(datos["autenticado"])
        self.assertFalse(
            datos["permisos"]["administrar"]
        )
        self.assertFalse(
            datos["puede_crear_equipos"]
        )

    def test_usuario_inactivo_sin_permisos(self):
        self.usuario.is_active = False
        self.usuario.save()

        self.assertFalse(
            tiene_rol(
                self.usuario,
                JEFE_DEPARTAMENTO,
            )
        )

        datos = construir_datos_sesion(
            self.usuario
        )

        self.assertFalse(datos["autenticado"])
