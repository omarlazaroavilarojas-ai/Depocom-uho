from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient


class ReportesTrazabilidadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = get_user_model().objects.create_superuser(
            username='admin_reportes_traza', email='reportes@example.org', password='PruebaSegura2026!')
        self.usuario = get_user_model().objects.create_user(
            username='sin_permiso_traza', password='PruebaSegura2026!')

    def test_anonimo_no_puede_descargar(self):
        for categoria in ('solicitudes', 'historial-solicitudes', 'trazabilidad-piezas'):
            r = self.client.get(f'/api/reportes/{categoria}.xlsx')
            self.assertIn(r.status_code, (401, 403))

    def test_usuario_sin_rol_no_puede_descargar(self):
        self.client.force_authenticate(self.usuario)
        for categoria in ('solicitudes', 'historial-solicitudes', 'trazabilidad-piezas'):
            r = self.client.get(f'/api/reportes/{categoria}.pdf')
            self.assertEqual(r.status_code, 403)

    def test_administrador_descarga_formatos(self):
        self.client.force_authenticate(self.admin)
        for categoria in ('solicitudes', 'historial-solicitudes', 'trazabilidad-piezas'):
            for formato, firma in (('pdf', b'%PDF'), ('xlsx', b'PK')):
                r = self.client.get(f'/api/reportes/{categoria}.{formato}')
                self.assertEqual(r.status_code, 200)
                self.assertTrue(r.content.startswith(firma))
