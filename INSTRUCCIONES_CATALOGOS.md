# DepoCom UHO — Administración de catálogos

## Instalación
1. Haz copia de seguridad de `backend/core` y `frontend`.
2. Copia el contenido de `backend/core` del ZIP sobre `backend/core` del proyecto.
3. Copia el contenido de `frontend` del ZIP sobre `frontend` del proyecto.
4. No reemplaces `backend/config/settings.py` ni tu `.env`.
5. Ejecuta en la carpeta `backend`:
   `.venv\Scripts\python.exe manage.py check`
   `.venv\Scripts\python.exe manage.py test core.test_catalogos_admin core.tests`
6. Reinicia Django: `.venv\Scripts\python.exe manage.py runserver`
7. Reinicia Vue: `npm run dev` desde `frontend`.
8. Inicia sesión con un usuario administrador y abre Administración.

## Funciones
- Sedes: consultar, crear, editar.
- Áreas: consultar, crear, editar; cada área requiere sede.
- Departamentos: consultar, crear, editar; cada departamento requiere área.
- Tipos de recursos: consultar, crear, editar.
- La lectura requiere iniciar sesión; la escritura exige rol ADMINISTRADOR o superusuario.
- No se incluye eliminación, para evitar borrar referencias institucionales existentes.
- Se preserva el proxy Vite existente y se utiliza cookie de sesión y CSRF.

## API
GET/POST /api/sedes/
GET/PATCH /api/sedes/<id>/
GET/POST /api/areas/
GET/PATCH /api/areas/<id>/
GET/POST /api/departamentos/
GET/PATCH /api/departamentos/<id>/
GET/POST /api/tipos-recursos/
GET/PATCH /api/tipos-recursos/<id>/

## Limitaciones
- El paquete no incluye backend/config ni base de datos.
- No se ha probado la ejecución contra tu PostgreSQL ni se ha compilado Vite en este entorno.
- Se actualizaron dos pruebas anteriores que esperaban HTTP 405 en POST anónimo; ahora la respuesta es HTTP 403 porque la escritura existe pero requiere autorización.
- No requiere migraciones: se utilizan modelos existentes.
