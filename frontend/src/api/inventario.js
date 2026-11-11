
import { prepararCSRF } from './sesion'

function obtenerCSRF() {
  const cookie = document.cookie
    .split(';')
    .map((valor) => valor.trim())
    .find((valor) => valor.startsWith('csrftoken='))

  return cookie
    ? decodeURIComponent(
        cookie.split('=').slice(1).join('=')
      )
    : ''
}

async function interpretarRespuesta(respuesta) {
  let datos = {}

  try {
    datos = await respuesta.json()
  } catch {
    throw new Error(
      `Respuesta inválida del servidor (${respuesta.status}).`
    )
  }

  if (!respuesta.ok) {
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

export async function obtenerInventario() {
  const respuesta = await fetch('/api/inventario/', {
    credentials: 'same-origin',
  })

  return interpretarRespuesta(respuesta)
}

async function enviarPieza(ruta, metodo, datos) {
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

  return interpretarRespuesta(respuesta)
}

export function crearPieza(datos) {
  return enviarPieza(
    '/api/inventario/',
    'POST',
    datos
  )
}

export function actualizarPieza(id, datos) {
  return enviarPieza(
    `/api/inventario/${id}/`,
    'PATCH',
    datos
  )
}
