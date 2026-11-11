# DepoCom UHO — Usuarios de demostración y roles

## Resultado del análisis
- El backend ya usa `django.contrib.auth.models.Group` y define siete roles institucionales en `core/roles.py`.
- Las API `/api/login/`, `/api/logout/` y `/api/sesion/` ya existen.
- Se corrigió el frontend para enviar `usuario` y `contrasena` como exige Django (antes enviaba `username` y `password`).
- Se filtra el menú lateral según los permisos que devuelve `/api/sesion/`.
- Los permisos efectivos deben seguir aplicándose en Django. El menú oculto no es una medida de seguridad por sí solo.

## Instalación en Windows
1. Haz copia de seguridad de tu proyecto.
2. Copia `backend/core/management/` dentro de `backend/core/` (fusionar carpetas, sin borrar lo demás).
3. Copia `backend/core/test_usuarios_demo.py` dentro de `backend/core/`.
4. Reemplaza `frontend/src/App.vue` con el archivo incluido.
5. No reemplaces tu `backend/config/settings.py` ni `.env`.
6. En la carpeta `backend`, con tu entorno virtual activado, ejecuta:

   python manage.py check
   python manage.py migrate
   python manage.py test core.test_usuarios_demo
   python manage.py crear_usuarios_demo --archivo credenciales_demo.txt

7. Guarda `backend/credenciales_demo.txt` en privado; contiene las claves de prueba. NO LO SUBAS A GITHUB.
8. Inicia Django y Vue normalmente. Prueba cerrar sesión y entrar con cada cuenta.

## Cuentas que crea
- `admin_demo`: Administrador del Sistema
- `solicitante_demo`: Jefe de Departamento
- `area_demo`: Jefe de Área
- `tecnico_demo`: Técnico de Soporte
- `soporte_demo`: Jefe de Soporte Técnico
- `economia_demo`: Jefe de Economía
- `auditor_demo`: Consultor

Cada contraseña es aleatoria. Si vuelves a ejecutar el comando, las cuentas existentes no se alteran ni se vuelven a imprimir sus claves.

## Observaciones
- Este bloque crea cuentas de prueba y adapta la navegación. NO implementa todavía una pantalla administrativa para gestionar usuarios reales.
- Algunas operaciones pueden requerir asignar sede, área o departamento al perfil institucional, porque el backend verifica alcance además de rol.
- Las pantallas de módulos existentes pueden mostrar mensajes de acceso denegado si el rol no tiene autorización para esa API. No se deben ampliar permisos para ocultar esos errores.
- Para la demostración, usa únicamente datos ficticios. El archivo de credenciales y el `.env` no deben subirse a GitHub.
