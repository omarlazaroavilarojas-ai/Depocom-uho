"""Pruebas de acceso y formatos de los nuevos reportes."""
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class ReportesFormatosTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = get_user_model().objects.create_user(username='reportes_test', password='prueba-segura-123')

    def test_sin_autenticacion_no_exporta(self):
        for ruta in ('/api/reportes/equipos-deposito.xlsx', '/api/reportes/equipos-deposito.pdf'):
            respuesta = self.client.get(ruta)
            self.assertIn(respuesta.status_code, (401, 403))

    def test_sin_rol_no_exporta(self):
        self.client.force_login(self.usuario)
        respuesta = self.client.get('/api/reportes/movimientos-piezas.xlsx')
        self.assertEqual(respuesta.status_code, 403)

    @patch('core.views_reportes._datos_equipos', return_value=(['Inventario', 'Estado'], [['A-123', 'disponible']]))
    @patch('core.views_reportes.tiene_rol', return_value=True)
    def test_excel_valido(self, _rol, _datos):
        from openpyxl import load_workbook
        from io import BytesIO
        self.client.force_login(self.usuario)
        respuesta = self.client.get('/api/reportes/equipos-deposito.xlsx')
        self.assertEqual(respuesta.status_code, 200)
        hoja = load_workbook(BytesIO(respuesta.content)).active
        self.assertEqual(hoja['A2'].value, 'A-123')

    @patch('core.views_reportes._datos_equipos', return_value=(['Inventario'], [['A-123']]))
    @patch('core.views_reportes.tiene_rol', return_value=True)
    def test_pdf_valido(self, _rol, _datos):
        self.client.force_login(self.usuario)
        respuesta = self.client.get('/api/reportes/equipos-deposito.pdf')
        self.assertEqual(respuesta.status_code, 200)
        self.assertTrue(respuesta.content.startswith(b'%PDF-'))
