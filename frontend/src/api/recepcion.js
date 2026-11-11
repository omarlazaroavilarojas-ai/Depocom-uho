const BASE = '/api'

function csrfCookie() {
  const match = document.cookie.split('; ').find(c => c.startsWith('csrftoken='))
  return match ? decodeURIComponent(match.slice(10)) : ''
}

async function respuesta(response) {
  const data = await response.json().catch(() => ({}))
  if (!response.ok) {
    const detalle = data.detail || data.detalle || data
    throw new Error(typeof detalle === 'string' ? detalle : JSON.stringify(detalle))
  }
  return data
}

export async function listarSolicitudesRecepcion() {
  return respuesta(await fetch(`${BASE}/solicitudes/`, { credentials: 'include' }))
}

export async function consultarRecepcion(id) {
  return respuesta(await fetch(`${BASE}/solicitudes/${encodeURIComponent(id)}/recepcion/`, { credentials: 'include' }))
}

export async function recibirEquipo(idSolicitud, idAsociacion, observaciones = '') {
  await respuesta(await fetch(`${BASE}/csrf/`, { credentials: 'include' }))
  return respuesta(await fetch(`${BASE}/solicitudes/${encodeURIComponent(idSolicitud)}/recepcion/`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfCookie() },
    body: JSON.stringify({ equipo_solicitud_id: idAsociacion, observaciones }),
  }))
}
