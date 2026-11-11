"""Pruebas de regresión de la cobertura mínima de Swagger/OpenAPI."""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class SwaggerCoberturaTests(TestCase):
    def setUp(self):
        self.usuario = get_user_model().objects.create_user(
            username='usuario_swagger', password='ClaveTemporal123!'
        )
        self.client.force_login(self.usuario)

    def test_esquema_incluye_operaciones_deposito_y_piezas(self):
        respuesta = self.client.get('/api/schema/', HTTP_ACCEPT='application/json')
        self.assertEqual(respuesta.status_code, 200)
        esquema = respuesta.json()
        rutas = esquema['paths']
        self.assertTrue(any('/api/deposito/equipos/' == p for p in rutas))
        self.assertTrue(any('/api/deposito/equipos/{id}/' == p for p in rutas))
        self.assertTrue(any('despieces' in p for p in rutas))
        self.assertTrue(any('traslados' in p for p in rutas))
        ids = [operacion['operationId'] for ruta in rutas.values()
               for verbo, operacion in ruta.items()
               if verbo.lower() in {'get', 'post', 'put', 'patch', 'delete'}]
        self.assertEqual(len(ids), len(set(ids)), 'operationId duplicados en OpenAPI')
