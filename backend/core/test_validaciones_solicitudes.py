
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status

from .models import Equipo, TipoRecurso
from .models_solicitudes import (
    SolicitudBaja,
    EquipoEnSolicitud,
)


class ValidacionesSolicitudesTests(TestCase):

    def setUp(self):
        User = get_user_model()

        self.admin = User.objects.create_superuser(
            username="admin_validaciones",
            email="admin_validaciones@example.com",
            password="ClavePrueba123!",
        )

        self.tipo = TipoRecurso.objects.create(
            nombre="Computadora"
        )

        self.equipo1 = Equipo.objects.create(
            no_inventario="INV-VAL-001",
            tipo_recurso=self.tipo,
        )

        self.equipo2 = Equipo.objects.create(
            no_inventario="INV-VAL-002",
            tipo_recurso=self.tipo,
        )

        self.solicitud = SolicitudBaja.objects.create(
            numero="SOL-VAL-001",
            solicitante=self.admin,
            observaciones="Original",
        )

        EquipoEnSolicitud.objects.create(
            solicitud=self.solicitud,
            equipo=self.equipo1,
        )

        self.client.force_login(self.admin)

        self.url_lista = "/api/solicitudes/"
        self.url_detalle = (
            f"/api/solicitudes/{self.solicitud.id}/"
        )

    def test_no_crea_solicitud_sin_equipos(self):
        respuesta = self.client.post(
            self.url_lista,
            data={
                "numero": "SOL-VAL-002",
                "equipos": [],
            },
            content_type="application/json",
        )

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertFalse(
            SolicitudBaja.objects.filter(
                numero="SOL-VAL-002"
            ).exists()
        )

    def test_no_crea_solicitud_con_equipos_repetidos(self):
        respuesta = self.client.post(
            self.url_lista,
            data={
                "numero": "SOL-VAL-002",
                "equipos": [
                    self.equipo1.id,
                    self.equipo1.id,
                ],
            },
            content_type="application/json",
        )

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_no_permite_numero_duplicado(self):
        respuesta = self.client.post(
            self.url_lista,
            data={
                "numero": "SOL-VAL-001",
                "equipos": [self.equipo2.id],
            },
            content_type="application/json",
        )

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_no_permite_numero_duplicado_con_minusculas(self):
        respuesta = self.client.post(
            self.url_lista,
            data={
                "numero": "sol-val-001",
                "equipos": [self.equipo2.id],
            },
            content_type="application/json",
        )

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_no_permite_numero_vacio(self):
        respuesta = self.client.post(
            self.url_lista,
            data={
                "numero": "   ",
                "equipos": [self.equipo2.id],
            },
            content_type="application/json",
        )

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_no_modifica_datos_si_equipos_son_invalidos(self):
        respuesta = self.client.patch(
            self.url_detalle,
            data={
                "observaciones": "Modificado",
                "equipos": [999999],
            },
            content_type="application/json",
        )

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.solicitud.refresh_from_db()

        self.assertEqual(
            self.solicitud.observaciones,
            "Original",
        )

        self.assertEqual(
            self.solicitud.equipos_asociados.count(),
            1,
        )

    def test_no_permite_cambiar_estado_por_api(self):
        respuesta = self.client.patch(
            self.url_detalle,
            data={
                "estado": "presentada",
            },
            content_type="application/json",
        )

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_200_OK,
        )

        self.solicitud.refresh_from_db()

        self.assertEqual(
            self.solicitud.estado,
            SolicitudBaja.Estado.BORRADOR,
        )

    def test_no_permite_cambiar_solicitante_por_api(self):
        User = get_user_model()

        otro = User.objects.create_user(
            username="otro_usuario",
            password="ClavePrueba123!",
        )

        respuesta = self.client.patch(
            self.url_detalle,
            data={
                "solicitante": otro.id,
            },
            content_type="application/json",
        )

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_200_OK,
        )

        self.solicitud.refresh_from_db()

        self.assertEqual(
            self.solicitud.solicitante_id,
            self.admin.id,
        )

    def test_conserva_equipos_si_solo_edita_observaciones(self):
        respuesta = self.client.patch(
            self.url_detalle,
            data={
                "observaciones": "Nueva observación",
            },
            content_type="application/json",
        )

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_200_OK,
        )

        self.assertTrue(
            EquipoEnSolicitud.objects.filter(
                solicitud=self.solicitud,
                equipo=self.equipo1,
            ).exists()
        )
