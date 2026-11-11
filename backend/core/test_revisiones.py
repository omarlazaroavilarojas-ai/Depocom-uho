
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status

from .models import Equipo, TipoRecurso
from .models_solicitudes import (
    SolicitudBaja,
    EquipoEnSolicitud,
    RevisionTecnica,
)


class RevisionesTecnicasTests(TestCase):

    def setUp(self):
        User = get_user_model()

        self.admin = User.objects.create_superuser(
            username="admin_revisiones",
            email="admin_revisiones@example.com",
            password="ClavePrueba123!",
        )

        self.usuario = User.objects.create_user(
            username="usuario_revisiones",
            password="ClavePrueba123!",
        )

        self.tipo = TipoRecurso.objects.create(
            nombre="Computadora"
        )

        self.equipo = Equipo.objects.create(
            no_inventario="INV-REV-001",
            tipo_recurso=self.tipo,
        )

        self.solicitud = SolicitudBaja.objects.create(
            numero="SOL-REV-001",
            solicitante=self.admin,
        )

        # Las revisiones solo pueden registrarse durante esta etapa.
        self.solicitud.estado = SolicitudBaja.Estado.EN_REVISION
        self.solicitud.save(update_fields=["estado"])

        self.asociacion = EquipoEnSolicitud.objects.create(
            solicitud=self.solicitud,
            equipo=self.equipo,
        )

        self.url = (
            f"/api/revisiones/{self.asociacion.id}/guardar/"
        )

        self.datos = {
            "condicion_fisica": "regular",
            "diagnostico": "Requiere evaluación adicional.",
            "observaciones": "Prueba técnica.",
        }

    def test_superusuario_registra_revision(self):
        self.client.force_login(self.admin)

        respuesta = self.client.put(
            self.url,
            data=self.datos,
            content_type="application/json",
        )

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_200_OK,
        )

        self.assertTrue(
            RevisionTecnica.objects.filter(
                equipo_solicitud=self.asociacion
            ).exists()
        )

    def test_superusuario_actualiza_revision(self):
        self.client.force_login(self.admin)

        self.client.put(
            self.url,
            data=self.datos,
            content_type="application/json",
        )

        respuesta = self.client.put(
            self.url,
            data={
                **self.datos,
                "diagnostico": "Diagnóstico actualizado.",
            },
            content_type="application/json",
        )

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            RevisionTecnica.objects.get(
                equipo_solicitud=self.asociacion
            ).diagnostico,
            "Diagnóstico actualizado.",
        )

    def test_usuario_normal_no_registra_revision(self):
        self.client.force_login(self.usuario)

        respuesta = self.client.put(
            self.url,
            data=self.datos,
            content_type="application/json",
        )

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_anonimo_no_registra_revision(self):
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

    def test_no_acepta_diagnostico_vacio(self):
        self.client.force_login(self.admin)

        respuesta = self.client.put(
            self.url,
            data={
                **self.datos,
                "diagnostico": "   ",
            },
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

        respuesta = self.client.put(
            self.url,
            data=self.datos,
            content_type="application/json",
        )

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
