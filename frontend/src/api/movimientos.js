
import { prepararCSRF } from './sesion'

const API_BASE = '/api/movimientos/'

function obtenerCookie(nombre) {
  const cookies = document.cookie.split(';')

  for (const cookie of cookies) {
    const [clave, ...valor] = cookie.trim().split('=')

    if (clave === nombre) {
      return decodeURIComponent(valor.join('='))
    }
  }

  return ''
}

async function procesarRespuesta(respuesta) {
  const datos = await respuesta.json().catch(() => null)

  if (!respuesta.ok) {
    let mensaje = 'Error al comunicarse con el servidor.'

    if (datos?.detail) {
      mensaje = String(datos.detail)
    } else if (datos && typeof datos === 'object') {
      mensaje = Object.entries(datos)
        .map(([campo, errores]) => {
          const texto = Array.isArray(errores)
            ? errores.join(', ')
            : String(errores)

          return `${campo}: ${texto}`
        })
        .join(' | ')
    }

    throw new Error(mensaje)
  }

  return datos
}

export async function obtenerMovimientos() {
  const respuesta = await fetch(API_BASE, {
    method: 'GET',
    credentials: 'include',
    headers: {
      Accept: 'application/json',
    },
  })

  return procesarRespuesta(respuesta)
}

export async function registrarMovimiento(datos) {
  await prepararCSRF()

  const respuesta = await fetch(
    `${API_BASE}registrar/`,
    {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': obtenerCookie('csrftoken'),
        Accept: 'application/json',
      },
      body: JSON.stringify(datos),
    }
  )

  return procesarRespuesta(respuesta)
}
