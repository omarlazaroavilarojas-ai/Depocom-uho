
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

async function interpretarRespuesta(respuesta) {
  let datos = {}

  try {
    datos = await respuesta.json()
  } catch {
    throw new Error(`Respuesta inválida del servidor (${respuesta.status}).`)
  }

  if (!respuesta.ok) {
    const detalle = datos.error || datos.detail

    if (detalle) {
      throw new Error(detalle)
    }

    const primerError = Object.values(datos)[0]

    throw new Error(
      Array.isArray(primerError)
        ? primerError.join(' ')
        : `Error HTTP ${respuesta.status}`
    )
  }

  return datos
}

export async function prepararCSRF() {
  const respuesta = await fetch('/api/csrf/', {
    credentials: 'same-origin',
  })
  return interpretarRespuesta(respuesta)
}

export async function consultarSesion() {
  const respuesta = await fetch('/api/sesion/', {
    credentials: 'same-origin',
  })
  return interpretarRespuesta(respuesta)
}

async function enviarDatos(ruta, metodo, datos = {}) {
  await prepararCSRF()

  const respuesta = await fetch(ruta, {
    method: metodo,
    credentials: 'same-origin',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': obtenerCookie('csrftoken'),
    },
    body: JSON.stringify(datos),
  })

  return interpretarRespuesta(respuesta)
}

export function iniciarSesion(usuario, contrasena) {
  return enviarDatos('/api/login/', 'POST', {
    usuario,
    contrasena,
  })
}

export function cerrarSesion() {
  return enviarDatos('/api/logout/', 'POST')
}

export function registrarEquipo(datos) {
  return enviarDatos('/api/equipos/', 'POST', datos)
}

export function actualizarEquipo(id, datos) {
  return enviarDatos(`/api/equipos/${id}/`, 'PUT', datos)
}
