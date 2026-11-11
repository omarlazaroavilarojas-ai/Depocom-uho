from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from .models import Sede, Area, Departamento, TipoRecurso


class CatalogosAdminTests(TestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_superuser(
            username="admin_catalogos", password="clave-segura-123",
            email="admin@example.test"
        )
        self.usuario = get_user_model().objects.create_user(
            username="lector_catalogos", password="clave-segura-123"
        )
        self.client = APIClient()
        self.sede = Sede.objects.create(nombre="Sede A", direccion="Calle A")
        self.area = Area.objects.create(nombre="Area A", sede=self.sede)

    def test_anonimo_no_puede_crear(self):
        r = self.client.post("/api/sedes/", {"nombre":"Nueva", "direccion":"Calle B"})
        self.assertIn(r.status_code, (401, 403))

    def test_usuario_no_admin_no_puede_editar(self):
        self.client.force_authenticate(self.usuario)
        r = self.client.patch(f"/api/sedes/{self.sede.pk}/", {"nombre":"Cambio"})
        self.assertEqual(r.status_code, 403)

    def test_admin_crea_y_edita_catalogos(self):
        self.client.force_authenticate(self.admin)
        r = self.client.post("/api/sedes/", {"nombre":"Sede B", "direccion":"Calle B"})
        self.assertEqual(r.status_code, 201, r.data)
        r = self.client.post("/api/areas/", {"nombre":"Area B", "sede":self.sede.pk})
        self.assertEqual(r.status_code, 201, r.data)
        r = self.client.post("/api/departamentos/", {
            "nombre":"Contabilidad", "tipo":"departamento", "area":self.area.pk,
            "centro_costo":"C1"
        })
        self.assertEqual(r.status_code, 201, r.data)
        pk = r.data["id"]
        r = self.client.patch(f"/api/departamentos/{pk}/", {"nombre":"Contabilidad Central"})
        self.assertEqual(r.status_code, 200, r.data)
        self.assertEqual(r.data["nombre"], "Contabilidad Central")
        r = self.client.post("/api/tipos-recursos/", {"nombre":"Impresora"})
        self.assertEqual(r.status_code, 201, r.data)
