
async function consultarAPI(ruta) {
  const respuesta = await fetch(ruta)

  if (!respuesta.ok) {
    throw new Error(
      `Error HTTP ${respuesta.status}`
    )
  }

  const datos = await respuesta.json()

  if (!Array.isArray(datos)) {
    throw new Error(
      'La API no devolvió una lista'
    )
  }

  return datos
}

export function obtenerSedes() {
  return consultarAPI('/api/sedes/')
}

export function obtenerTiposRecursos() {
  return consultarAPI('/api/tipos-recursos/')
}

export function obtenerDepartamentos() {
  return consultarAPI('/api/departamentos/')
}

export function obtenerEquipos() {
  return consultarAPI('/api/equipos/')
}
