
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status

from .models_inventario import PiezaDeposito
from .models_movimientos import MovimientoInventario


class ConsolidacionInventarioTests(TestCase):

    def setUp(self):
        User = get_user_model()

        self.admin = User.objects.create_superuser(
            username="admin_consolidacion",
            email="consolidacion@example.com",
            password="ClavePrueba123!",
        )

        self.client.force_login(self.admin)

    def test_creacion_registra_existencia_inicial(self):
        respuesta = self.client.post(
            "/api/inventario/",
            data={
                "codigo": "SSD-CON-001",
                "nombre": "Disco SSD",
                "cantidad": 8,
                "estado": "disponible",
            },
            content_type="application/json",
        )

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_201_CREATED,
        )

        pieza = PiezaDeposito.objects.get(
            codigo="SSD-CON-001"
        )

        movimiento = MovimientoInventario.objects.get(
            pieza=pieza
        )

        self.assertEqual(
            movimiento.existencia_anterior,
            0,
        )

        self.assertEqual(
            movimiento.existencia_posterior,
            8,
        )

    def test_no_permite_modificar_cantidad(self):
        pieza = PiezaDeposito.objects.create(
            codigo="RAM-CON-001",
            nombre="Memoria RAM",
            cantidad=5,
        )

        respuesta = self.client.patch(
            f"/api/inventario/{pieza.id}/",
            data={"cantidad": 100},
            content_type="application/json",
        )

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        pieza.refresh_from_db()

        self.assertEqual(pieza.cantidad, 5)

    def test_edicion_otros_campos_funciona(self):
        pieza = PiezaDeposito.objects.create(
            codigo="CPU-CON-001",
            nombre="Procesador",
            cantidad=2,
        )

        respuesta = self.client.patch(
            f"/api/inventario/{pieza.id}/",
            data={"ubicacion": "Estante C"},
            content_type="application/json",
        )

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_200_OK,
        )

        pieza.refresh_from_db()

        self.assertEqual(
            pieza.ubicacion,
            "Estante C",
        )
