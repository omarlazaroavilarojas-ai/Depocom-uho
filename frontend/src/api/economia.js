const BASE = '/api';

function csrfCookie() {
  const cookie = document.cookie.split('; ').find((c) => c.startsWith('csrftoken='));
  return cookie ? decodeURIComponent(cookie.slice('csrftoken='.length)) : '';
}

async function parseResponse(response) {
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = data.detail || data.detalle || data.estado || data.comentario || data;
    throw new Error(typeof detail === 'string' ? detail : JSON.stringify(detail));
  }
  return data;
}

export async function listarSolicitudesEconomia() {
  return parseResponse(await fetch(`${BASE}/solicitudes/`, { credentials: 'include' }));
}

export async function ejecutarAccionEconomica(id, accion, comentario = '') {
  const rutas = {
    remitir: 'remitir-economia',
    iniciar: 'iniciar-economia',
    aprobar: 'aprobar-economia',
  };
  if (!rutas[accion]) throw new Error('Acción económica no reconocida.');
  await parseResponse(await fetch(`${BASE}/csrf/`, { credentials: 'include' }));
  return parseResponse(await fetch(`${BASE}/solicitudes/${encodeURIComponent(id)}/${rutas[accion]}/`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfCookie() },
    body: JSON.stringify({ comentario }),
  }));
}
