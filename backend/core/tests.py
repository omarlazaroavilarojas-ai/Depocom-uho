
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status

from .models import (
    Sede,
    TipoRecurso,
    Area,
    Departamento,
    Equipo,
)


# ============================================================
# PRUEBAS DE LA API DE SEDES
# ============================================================

class SedeAPITests(TestCase):

    def setUp(self):
        self.sede = Sede.objects.create(
            nombre="Sede de prueba",
            direccion="Dirección de prueba",
        )

    def test_listar_sedes(self):
        respuesta = self.client.get("/api/sedes/")

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_200_OK,
        )

        datos = respuesta.json()

        self.assertIsInstance(datos, list)
        self.assertEqual(len(datos), 1)

        self.assertEqual(
            datos[0]["nombre"],
            "Sede de prueba",
        )

    def test_no_permitir_crear_sede_anonimo(self):
        respuesta = self.client.post(
            "/api/sedes/",
            {
                "nombre": "Otra sede",
                "direccion": "Otra dirección",
            },
        )

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_403_FORBIDDEN,
        )


# ============================================================
# PRUEBAS DE LA API DE TIPOS DE RECURSOS
# ============================================================

class TipoRecursoAPITests(TestCase):

    def setUp(self):
        self.tipo = TipoRecurso.objects.create(
            nombre="Computadora",
        )

    def test_listar_tipos_recursos(self):
        respuesta = self.client.get(
            "/api/tipos-recursos/"
        )

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_200_OK,
        )

        datos = respuesta.json()

        self.assertIsInstance(datos, list)
        self.assertEqual(len(datos), 1)

        self.assertEqual(
            datos[0]["nombre"],
            "Computadora",
        )

    def test_no_permitir_crear_tipo_anonimo(self):
        respuesta = self.client.post(
            "/api/tipos-recursos/",
            {
                "nombre": "Monitor",
            },
        )

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_403_FORBIDDEN,
        )


# ============================================================
# PRUEBAS DEL MODELO EQUIPO
# ============================================================

class EquipoModelTests(TestCase):

    def setUp(self):
        self.sede = Sede.objects.create(
            nombre="Sede Central",
            direccion="Holguín",
        )

        self.area = Area.objects.create(
            nombre="Área de prueba",
            descripcion="Área utilizada para pruebas",
            sede=self.sede,
        )

        self.departamento = Departamento.objects.create(
            nombre="Departamento de prueba",
            tipo=Departamento.Tipo.DEPARTAMENTO,
            area=self.area,
            centro_costo="CC-001",
        )

        self.tipo_recurso = TipoRecurso.objects.create(
            nombre="Computadora",
        )

    def test_crear_equipo(self):
        equipo = Equipo.objects.create(
            no_inventario="INV-001",
            tipo_recurso=self.tipo_recurso,
            marca="Dell",
            modelo="OptiPlex",
            no_serie="SER-001",
        )

        self.assertEqual(
            Equipo.objects.count(),
            1,
        )

        self.assertEqual(
            equipo.no_inventario,
            "INV-001",
        )

        self.assertEqual(
            equipo.marca,
            "Dell",
        )

        self.assertEqual(
            str(equipo),
            "INV-001 - Computadora",
        )

    def test_relacion_equipo_departamento(self):
        equipo = Equipo.objects.create(
            no_inventario="INV-002",
            tipo_recurso=self.tipo_recurso,
            departamento=self.departamento,
        )

        self.assertEqual(
            equipo.departamento,
            self.departamento,
        )

        self.assertIn(
            equipo,
            self.departamento.equipos.all(),
        )

    def test_equipo_sin_departamento(self):
        equipo = Equipo.objects.create(
            no_inventario="INV-003",
            tipo_recurso=self.tipo_recurso,
            departamento=None,
        )

        self.assertIsNone(
            equipo.departamento,
        )


# ============================================================
# PRUEBAS DE CONSULTA DE EQUIPOS POR API
# ============================================================

class EquipoAPITests(TestCase):

    def setUp(self):
        self.tipo_recurso = TipoRecurso.objects.create(
            nombre="Computadora",
        )

        self.equipo = Equipo.objects.create(
            no_inventario="INV-001",
            tipo_recurso=self.tipo_recurso,
            marca="Dell",
            modelo="OptiPlex",
            no_serie="SER-001",
        )

    def test_listar_equipos(self):
        respuesta = self.client.get(
            "/api/equipos/"
        )

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_200_OK,
        )

        datos = respuesta.json()

        self.assertIsInstance(datos, list)
        self.assertEqual(len(datos), 1)

        self.assertEqual(
            datos[0]["no_inventario"],
            "INV-001",
        )

        self.assertEqual(
            datos[0]["tipo_recurso_nombre"],
            "Computadora",
        )

    def test_equipo_sin_departamento_en_api(self):
        respuesta = self.client.get(
            "/api/equipos/"
        )

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_200_OK,
        )

        datos = respuesta.json()

        self.assertIsNone(
            datos[0]["departamento_nombre"],
        )


# ============================================================
# PRUEBA DE LISTADO VACÍO DE EQUIPOS
# ============================================================

class EquipoAPIListadoVacioTests(TestCase):

    def test_listado_vacio(self):
        respuesta = self.client.get(
            "/api/equipos/"
        )

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            respuesta.json(),
            [],
        )


# ============================================================
# PRUEBAS DE CREACIÓN DE EQUIPOS POR API
# CLASE 26
# ============================================================

class EquipoCreacionAPITests(TestCase):

    def setUp(self):
        self.tipo = TipoRecurso.objects.create(
            nombre="Computadora de prueba",
        )

        User = get_user_model()

        self.superusuario = User.objects.create_superuser(
            username="admin_prueba",
            email="admin@example.com",
            password="ClaveTemporalPrueba_123!",
        )

        self.usuario_normal = User.objects.create_user(
            username="usuario_prueba",
            password="ClaveTemporalPrueba_123!",
        )

        self.datos = {
            "no_inventario": "INV-NUEVO-001",
            "tipo_recurso": self.tipo.id,
            "marca": "Dell",
            "modelo": "OptiPlex",
            "no_serie": "SER-NUEVO-001",
        }

    def test_anonimo_no_puede_crear_equipo(self):
        respuesta = self.client.post(
            "/api/equipos/",
            self.datos,
        )

        self.assertIn(
            respuesta.status_code,
            [
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            ],
        )

        self.assertEqual(
            Equipo.objects.count(),
            0,
        )

    def test_usuario_normal_no_puede_crear_equipo(self):
        self.client.force_login(
            self.usuario_normal
        )

        respuesta = self.client.post(
            "/api/equipos/",
            self.datos,
        )

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.assertEqual(
            Equipo.objects.count(),
            0,
        )

    def test_superusuario_puede_crear_equipo(self):
        self.client.force_login(
            self.superusuario
        )

        respuesta = self.client.post(
            "/api/equipos/",
            self.datos,
        )

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            Equipo.objects.count(),
            1,
        )

        equipo = Equipo.objects.first()

        self.assertEqual(
            equipo.no_inventario,
            "INV-NUEVO-001",
        )

        self.assertEqual(
            equipo.marca,
            "Dell",
        )

    def test_rechazar_inventario_vacio(self):
        self.client.force_login(
            self.superusuario
        )

        datos = self.datos.copy()
        datos["no_inventario"] = "   "

        respuesta = self.client.post(
            "/api/equipos/",
            datos,
        )

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            Equipo.objects.count(),
            0,
        )

    def test_rechazar_tipo_inexistente(self):
        self.client.force_login(
            self.superusuario
        )

        datos = self.datos.copy()
        datos["tipo_recurso"] = 999999

        respuesta = self.client.post(
            "/api/equipos/",
            datos,
        )

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            Equipo.objects.count(),
            0,
        )
