
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

export async function guardarRevision(equipoSolicitudId, datos) {
  await prepararCSRF()

  const respuesta = await fetch(
    `/api/revisiones/${equipoSolicitudId}/guardar/`,
    {
      method: 'PUT',
      credentials: 'same-origin',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': obtenerCSRF(),
      },
      body: JSON.stringify(datos),
    }
  )

  const resultado = await respuesta.json()

  if (!respuesta.ok) {
    const errores = Object.entries(resultado)
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

  return resultado
}
