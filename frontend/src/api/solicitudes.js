
import { prepararCSRF } from './sesion'

function obtenerCSRF() {
  const cookie = document.cookie
    .split(';')
    .map((valor) => valor.trim())
    .find((valor) => valor.startsWith('csrftoken='))

  return cookie
    ? decodeURIComponent(cookie.split('=').slice(1).join('='))
    : ''
}

async function interpretar(respuesta) {
  let datos = {}

  try {
    datos = await respuesta.json()
  } catch {
    throw new Error(
      `El servidor devolvió una respuesta inválida (${respuesta.status}).`
    )
  }

  if (!respuesta.ok) {
    const detalle = datos.detail || datos.error

    if (detalle) {
      throw new Error(
        Array.isArray(detalle) ? detalle.join(' ') : String(detalle)
      )
    }

    const errores = Object.entries(datos)
      .map(([campo, mensajes]) => {
        const texto = Array.isArray(mensajes)
          ? mensajes.join(' ')
          : String(mensajes)

        return `${campo}: ${texto}`
      })
      .join(' | ')

    throw new Error(
      errores || `Error HTTP ${respuesta.status}`
    )
  }

  return datos
}

export async function obtenerSolicitudes() {
  const respuesta = await fetch('/api/solicitudes/', {
    credentials: 'same-origin',
  })

  return interpretar(respuesta)
}

async function enviarSolicitud(ruta, metodo, datos) {
  await prepararCSRF()

  const respuesta = await fetch(ruta, {
    method: metodo,
    credentials: 'same-origin',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': obtenerCSRF(),
    },
    body: JSON.stringify(datos),
  })

  return interpretar(respuesta)
}

export function crearSolicitud(datos) {
  return enviarSolicitud(
    '/api/solicitudes/',
    'POST',
    datos
  )
}

export function actualizarSolicitud(id, datos) {
  return enviarSolicitud(
    `/api/solicitudes/${id}/`,
    'PATCH',
    datos
  )
}
