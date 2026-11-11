
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status

from .models_inventario import PiezaDeposito


class InventarioTests(TestCase):

    def setUp(self):
        User = get_user_model()

        self.admin = User.objects.create_superuser(
            username="admin_inventario",
            email="admin_inventario@example.com",
            password="ClavePrueba123!",
        )

        self.usuario = User.objects.create_user(
            username="usuario_inventario",
            password="ClavePrueba123!",
        )

        self.pieza = PiezaDeposito.objects.create(
            codigo="RAM-001",
            nombre="Memoria RAM",
            cantidad=5,
            estado="disponible",
            ubicacion="Estante A",
        )

        self.datos = {
            "codigo": "SSD-001",
            "nombre": "Unidad SSD",
            "cantidad": 3,
            "estado": "disponible",
            "ubicacion": "Estante B",
        }

    def test_usuario_autenticado_consulta_inventario(self):
        self.client.force_login(self.usuario)

        respuesta = self.client.get("/api/inventario/")

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_200_OK,
        )

    def test_anonimo_no_consulta_inventario(self):
        respuesta = self.client.get("/api/inventario/")

        self.assertIn(
            respuesta.status_code,
            (
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            ),
        )

    def test_superusuario_crea_pieza(self):
        self.client.force_login(self.admin)

        respuesta = self.client.post(
            "/api/inventario/",
            data=self.datos,
            content_type="application/json",
        )

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            PiezaDeposito.objects.filter(
                codigo="SSD-001"
            ).exists()
        )

    def test_usuario_normal_no_crea_pieza(self):
        self.client.force_login(self.usuario)

        respuesta = self.client.post(
            "/api/inventario/",
            data=self.datos,
            content_type="application/json",
        )

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_superusuario_no_modifica_cantidad_directamente(self):
        self.client.force_login(self.admin)

        respuesta = self.client.patch(
            f"/api/inventario/{self.pieza.id}/",
            data={"cantidad": 10},
            content_type="application/json",
        )

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.pieza.refresh_from_db()

        self.assertEqual(self.pieza.cantidad, 5)

    def test_rechaza_cantidad_negativa(self):
        self.client.force_login(self.admin)

        respuesta = self.client.post(
            "/api/inventario/",
            data={
                **self.datos,
                "cantidad": -2,
            },
            content_type="application/json",
        )

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_rechaza_codigo_duplicado(self):
        self.client.force_login(self.admin)

        respuesta = self.client.post(
            "/api/inventario/",
            data={
                **self.datos,
                "codigo": "ram-001",
            },
            content_type="application/json",
        )

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_rechaza_nombre_vacio(self):
        self.client.force_login(self.admin)

        respuesta = self.client.post(
            "/api/inventario/",
            data={
                **self.datos,
                "nombre": "   ",
            },
            content_type="application/json",
        )

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
