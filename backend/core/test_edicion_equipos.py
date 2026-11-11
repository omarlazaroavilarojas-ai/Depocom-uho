
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status

from .models import TipoRecurso, Equipo


class EquipoEdicionAPITests(TestCase):

    def setUp(self):
        self.tipo = TipoRecurso.objects.create(
            nombre="Computadora"
        )

        self.equipo = Equipo.objects.create(
            no_inventario="INV-001",
            tipo_recurso=self.tipo,
            marca="Dell",
            modelo="OptiPlex",
        )

        User = get_user_model()

        self.superusuario = User.objects.create_superuser(
            username="admin_edicion",
            email="admin@example.com",
            password="ClavePrueba123!",
        )

        self.usuario_normal = User.objects.create_user(
            username="usuario_edicion",
            password="ClavePrueba123!",
        )

        self.url = f"/api/equipos/{self.equipo.id}/"

        self.datos = {
            "no_inventario": "INV-001",
            "tipo_recurso": self.tipo.id,
            "marca": "Lenovo",
            "modelo": "ThinkCentre",
            "no_serie": "SER-001",
            "departamento": None,
        }

    def test_consultar_detalles(self):
        respuesta = self.client.get(self.url)

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            respuesta.json()["no_inventario"],
            "INV-001",
        )

    def test_anonimo_no_puede_editar(self):
        respuesta = self.client.put(
            self.url,
            data=self.datos,
            content_type="application/json",
        )

        self.assertIn(
            respuesta.status_code,
            (
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            ),
        )

    def test_usuario_normal_no_puede_editar(self):
        self.client.force_login(self.usuario_normal)

        respuesta = self.client.put(
            self.url,
            data=self.datos,
            content_type="application/json",
        )

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_superusuario_puede_editar(self):
        self.client.force_login(self.superusuario)

        respuesta = self.client.put(
            self.url,
            data=self.datos,
            content_type="application/json",
        )

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_200_OK,
        )

        self.equipo.refresh_from_db()

        self.assertEqual(
            self.equipo.marca,
            "Lenovo",
        )

    def test_edicion_invalida(self):
        self.client.force_login(self.superusuario)

        datos = {
            **self.datos,
            "no_inventario": "   ",
        }

        respuesta = self.client.put(
            self.url,
            data=datos,
            content_type="application/json",
        )

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.equipo.refresh_from_db()

        self.assertEqual(
            self.equipo.no_inventario,
            "INV-001",
        )
