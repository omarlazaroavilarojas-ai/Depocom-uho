# DepoCom UHO — Módulo de despiece

Este paquete contiene el frontend actualizado, sin cambios en el backend. Se comprobó que `core(2).zip` ya incluye las rutas y modelos de despiece, piezas recuperadas y tipos de pieza.

## Instalar
1. Guarda una copia de tu frontend actual.
2. Copia el contenido de la carpeta `frontend` de este ZIP dentro de tu carpeta `frontend`, reemplazando los archivos coincidentes.
3. NO copies `backend` ni ejecutes migraciones: el backend actual ya tiene la funcionalidad necesaria.
4. En la carpeta frontend ejecuta `npm install` si faltan dependencias, y luego `npm run dev`.
5. Mantén Django ejecutándose en el puerto 8000 y Vue en el 5173.

## Probar
1. Entra con un administrador. Abre Despiece de equipos.
2. Crea un tipo de pieza, por ejemplo Memoria RAM. No confundir con Tipos de recursos.
3. Selecciona un equipo recibido en depósito, indica fecha sugerida y justificación, y solicita el despiece.
4. Aprueba la solicitud como administrador o jefe de soporte.
5. Registra una pieza con código único, tipo y estado reutilizable. Confirma que aparece en Piezas recuperadas.

El backend restringe las acciones por rol: técnicos y administradores solicitan/ejecutan; jefes de soporte y administradores deciden. La lectura también depende de los permisos y de la sede.

## Importante
- El módulo usa `/api/almacen/piezas/` (piezas recuperadas), que es distinto de `/api/inventario/` (inventario de piezas ya existente). No se modificó la lógica backend ni se mezclaron ambos almacenes.
- No se ejecutó la compilación del frontend aquí porque `vite` no está instalado en este entorno. Puedes validarla en tu PC con `npm run build`.
