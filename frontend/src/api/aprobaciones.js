
const API_BASE = "/api";

function obtenerCookie(nombre) {
  const cookies = document.cookie.split(";");

  for (const cookie of cookies) {
    const [clave, ...valor] = cookie.trim().split("=");

    if (clave === nombre) {
      return decodeURIComponent(valor.join("="));
    }
  }

  return "";
}

async function prepararCSRF() {
  const respuesta = await fetch(`${API_BASE}/csrf/`, {
    credentials: "include",
  });

  if (!respuesta.ok) {
    throw new Error("No se pudo preparar la sesión CSRF.");
  }
}

async function peticion(url, metodo = "POST", datos = null) {
  await prepararCSRF();

  const respuesta = await fetch(`${API_BASE}${url}`, {
    method: metodo,
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": obtenerCookie("csrftoken"),
    },
    ...(datos !== null ? { body: JSON.stringify(datos) } : {}),
  });

  const resultado = await respuesta.json().catch(() => ({}));

  if (!respuesta.ok) {
    const detalle =
      resultado.detail ||
      resultado.detalle ||
      resultado.estado ||
      resultado.comentario ||
      `Error HTTP ${respuesta.status}`;

    throw new Error(
      typeof detalle === "string"
        ? detalle
        : JSON.stringify(detalle)
    );
  }

  return resultado;
}

export function presentarSolicitud(id) {
  return peticion(`/solicitudes/${id}/presentar/`);
}

export function decidirSolicitudArea(id, decision, comentario) {
  return peticion(`/solicitudes/${id}/decision-area/`, "POST", {
    decision,
    comentario,
  });
}

export function iniciarRevisionTecnica(id) {
  return peticion(`/solicitudes/${id}/iniciar-revision/`);
}

export function guardarRevisionTecnica(id, datos) {
  return peticion(`/revisiones/${id}/guardar/`, "PUT", datos);
}

export function aprobarRevisionTecnica(id) {
  return peticion(`/solicitudes/${id}/aprobar-revision/`);
}

export async function obtenerSolicitudes() {
  const respuesta = await fetch(`${API_BASE}/solicitudes/`, {
    credentials: "include",
  });

  if (!respuesta.ok) {
    throw new Error("No se pudieron cargar las solicitudes.");
  }

  const datos = await respuesta.json();

  return Array.isArray(datos) ? datos : datos.results || [];
}
