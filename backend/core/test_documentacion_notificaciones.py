from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from .models_ciclo_piezas import Notificacion
from .signals import emitir


class DocumentacionNotificacionesTests(TestCase):
    def setUp(self):
        self.usuario = get_user_model().objects.create_user(username='prueba_docs', password='ClaveTemporal123!')

    def test_documentacion_requiere_autenticacion(self):
        for url in ('/api/schema/', '/api/docs/'):
            respuesta = self.client.get(url)
            self.assertIn(respuesta.status_code, (301, 302, 403))

    def test_documentacion_usuario_autenticado(self):
        self.client.force_login(self.usuario)
        self.assertEqual(self.client.get('/api/schema/').status_code, 200)
        self.assertEqual(self.client.get('/api/docs/').status_code, 200)

    def test_notificacion_no_duplica_destinatarios(self):
        emitir([self.usuario, self.usuario], 'Aviso', 'Mensaje')
        self.assertEqual(Notificacion.objects.filter(usuario=self.usuario).count(), 1)
