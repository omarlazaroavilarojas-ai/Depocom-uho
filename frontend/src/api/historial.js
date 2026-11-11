
export async function obtenerHistorialSolicitud(solicitudId) {
  const respuesta = await fetch(
    `/api/solicitudes/${solicitudId}/historial/`,
    {
      credentials: 'same-origin',
    }
  )

  const datos = await respuesta.json()

  if (!respuesta.ok) {
    throw new Error(
      datos.detail ||
      `Error al consultar el historial (${respuesta.status}).`
    )
  }

  return datos
}
