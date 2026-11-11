
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status

from .models import Equipo, TipoRecurso, Sede, Area, Departamento
from .models_solicitudes import SolicitudBaja
from .models_historial import HistorialSolicitud


class HistorialSolicitudTests(TestCase):

    def setUp(self):
        User = get_user_model()

        self.admin = User.objects.create_superuser(
            username="admin_historial",
            email="admin_historial@example.com",
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

        self.equipo = Equipo.objects.create(
            no_inventario="INV-HIS-001",
            tipo_recurso=self.tipo,
            departamento=self.departamento,
        )

        self.client.force_login(self.admin)

    def crear_solicitud(self):
        return self.client.post(
            "/api/solicitudes/",
            data={
                "numero": "SOL-HIS-001",
                "observaciones": "Solicitud inicial",
                "equipos": [self.equipo.id],
            },
            content_type="application/json",
        )

    def test_creacion_registra_evento(self):
        respuesta = self.crear_solicitud()

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_201_CREATED,
        )

        solicitud = SolicitudBaja.objects.get(
            numero="SOL-HIS-001"
        )

        self.assertTrue(
            HistorialSolicitud.objects.filter(
                solicitud=solicitud,
                accion=HistorialSolicitud.Accion.CREACION,
            ).exists()
        )

    def test_edicion_registra_evento(self):
        self.crear_solicitud()

        solicitud = SolicitudBaja.objects.get(
            numero="SOL-HIS-001"
        )

        respuesta = self.client.patch(
            f"/api/solicitudes/{solicitud.id}/",
            data={
                "observaciones": "Solicitud modificada",
            },
            content_type="application/json",
        )

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_200_OK,
        )

        self.assertTrue(
            HistorialSolicitud.objects.filter(
                solicitud=solicitud,
                accion=HistorialSolicitud.Accion.EDICION,
            ).exists()
        )

    def test_consulta_historial(self):
        self.crear_solicitud()

        solicitud = SolicitudBaja.objects.get(
            numero="SOL-HIS-001"
        )

        respuesta = self.client.get(
            f"/api/solicitudes/{solicitud.id}/historial/"
        )

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(respuesta.json()),
            1,
        )

    def test_anonimo_no_consulta_historial(self):
        self.crear_solicitud()

        solicitud = SolicitudBaja.objects.get(
            numero="SOL-HIS-001"
        )

        self.client.logout()

        respuesta = self.client.get(
            f"/api/solicitudes/{solicitud.id}/historial/"
        )

        self.assertIn(
            respuesta.status_code,
            (
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            ),
        )

