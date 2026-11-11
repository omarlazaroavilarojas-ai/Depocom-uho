
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status

from .models import Equipo, TipoRecurso, Sede, Area, Departamento
from .models_solicitudes import (
    SolicitudBaja,
    EquipoEnSolicitud,
)


class GestionSolicitudesTests(TestCase):

    def setUp(self):
        User = get_user_model()

        self.admin = User.objects.create_superuser(
            username="admin_solicitudes",
            email="admin_solicitudes@example.com",
            password="ClavePrueba123!",
        )

        self.usuario = User.objects.create_user(
            username="usuario_solicitudes",
            password="ClavePrueba123!",
        )

        self.tipo = TipoRecurso.objects.create(
            nombre="Computadora"
        )

        self.sede = Sede.objects.create(nombre="Sede de pruebas", direccion="Holguín")
        self.area = Area.objects.create(nombre="Área de pruebas", sede=self.sede)
        self.departamento = Departamento.objects.create(
            nombre="Departamento de pruebas",
            tipo=Departamento.Tipo.DEPARTAMENTO,
            area=self.area,
        )

        self.equipo1 = Equipo.objects.create(
            no_inventario="INV-SOL-001",
            tipo_recurso=self.tipo,
            departamento=self.departamento,
        )

        self.equipo2 = Equipo.objects.create(
            no_inventario="INV-SOL-002",
            tipo_recurso=self.tipo,
            departamento=self.departamento,
        )

        self.solicitud = SolicitudBaja.objects.create(
            numero="SOL-TEST-001",
            solicitante=self.admin,
            departamento=self.departamento,
            observaciones="Solicitud inicial",
        )

        EquipoEnSolicitud.objects.create(
            solicitud=self.solicitud,
            equipo=self.equipo1,
        )

        self.url = f"/api/solicitudes/{self.solicitud.id}/"

    def test_usuario_autenticado_consulta_detalle(self):
        self.client.force_login(self.usuario)

        respuesta = self.client.get(self.url)

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_superusuario_consulta_detalle(self):
        self.client.force_login(self.admin)
        respuesta = self.client.get(self.url)
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(
            respuesta.json()["numero"],
            "SOL-TEST-001",
        )

    def test_anonimo_no_consulta_detalle(self):
        respuesta = self.client.get(self.url)

        self.assertIn(
            respuesta.status_code,
            (
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            ),
        )

    def test_superusuario_edita_observaciones(self):
        self.client.force_login(self.admin)

        respuesta = self.client.patch(
            self.url,
            data={
                "observaciones": "Observaciones actualizadas",
            },
            content_type="application/json",
        )

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_200_OK,
        )

        self.solicitud.refresh_from_db()

        self.assertEqual(
            self.solicitud.observaciones,
            "Observaciones actualizadas",
        )

    def test_superusuario_cambia_equipos(self):
        self.client.force_login(self.admin)

        respuesta = self.client.patch(
            self.url,
            data={
                "equipos": [self.equipo2.id],
            },
            content_type="application/json",
        )

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_200_OK,
        )

        ids = list(
            self.solicitud.equipos_asociados.values_list(
                "equipo_id",
                flat=True,
            )
        )

        self.assertEqual(ids, [self.equipo2.id])

    def test_usuario_normal_no_edita(self):
        self.client.force_login(self.usuario)

        respuesta = self.client.patch(
            self.url,
            data={
                "observaciones": "Cambio no autorizado",
            },
            content_type="application/json",
        )

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_anonimo_no_edita(self):
        respuesta = self.client.patch(
            self.url,
            data={
                "observaciones": "Cambio anónimo",
            },
            content_type="application/json",
        )

        self.assertIn(
            respuesta.status_code,
            (
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            ),
        )

    def test_no_permite_equipos_duplicados(self):
        self.client.force_login(self.admin)

        respuesta = self.client.patch(
            self.url,
            data={
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

    def test_no_permite_lista_vacia(self):
        self.client.force_login(self.admin)

        respuesta = self.client.patch(
            self.url,
            data={"equipos": []},
            content_type="application/json",
        )

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_no_edita_solicitud_presentada(self):
        self.solicitud.estado = (
            SolicitudBaja.Estado.PRESENTADA
        )
        self.solicitud.save()

        self.client.force_login(self.admin)

        respuesta = self.client.patch(
            self.url,
            data={
                "observaciones": "Intento de modificación",
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
            "Solicitud inicial",
        )
