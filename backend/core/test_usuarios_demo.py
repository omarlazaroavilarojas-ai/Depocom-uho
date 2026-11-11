from io import StringIO
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.test import TestCase
from .management.commands.crear_usuarios_demo import CUENTAS
from .roles import obtener_roles_usuario

class UsuariosDemoTests(TestCase):
    def test_creacion_y_roles(self):
        salida = StringIO()
        call_command('crear_usuarios_demo', stdout=salida)
        User = get_user_model()
        for nombre, rol in CUENTAS:
            usuario = User.objects.get(username=nombre)
            self.assertTrue(usuario.has_usable_password())
            self.assertEqual(obtener_roles_usuario(usuario), [rol])
            self.assertFalse(usuario.is_superuser)
        call_command('crear_usuarios_demo', stdout=StringIO())
        self.assertEqual(User.objects.filter(username__endswith='_demo').count(), 7)
