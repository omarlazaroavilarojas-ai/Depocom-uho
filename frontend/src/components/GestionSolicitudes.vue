
<script setup>
import { computed, ref, watch } from 'vue'

import {
  obtenerSolicitudes,
  crearSolicitud,
  actualizarSolicitud,
} from '../api/solicitudes'

import { guardarRevision } from '../api/revisiones'

import HistorialSolicitud from './HistorialSolicitud.vue'

const props = defineProps({
  equipos: {
    type: Array,
    required: true,
  },
  sesion: {
    type: Object,
    required: true,
  },
})

// Formulario de solicitudes
const numero = ref('')
const observaciones = ref('')
const equiposSeleccionados = ref([])

const solicitudes = ref([])
const solicitudEditar = ref(null)

// Formulario de revisiones técnicas
const revisionEditando = ref(null)

const condicionFisica = ref('no_evaluada')
const diagnostico = ref('')
const observacionesTecnicas = ref('')

// Historial
const historialAbierto = ref(null)

// Estados de carga
const cargando = ref(false)
const guardando = ref(false)
const guardandoRevision = ref(false)

// Mensajes
const error = ref('')
const mensaje = ref('')

// Permisos
const puedeGestionar = computed(() => {
  return Boolean(
    props.sesion.autenticado &&
    props.sesion.puede_crear_equipos
  )
})

const modoEdicion = computed(() => {
  return solicitudEditar.value !== null
})

const tituloFormulario = computed(() => {
  return modoEdicion.value
    ? `Editar solicitud ${solicitudEditar.value.numero}`
    : 'Nueva solicitud de baja'
})

// Consultar solicitudes
async function cargarSolicitudes() {
  if (!props.sesion.autenticado) {
    solicitudes.value = []
    return
  }

  cargando.value = true

  try {
    solicitudes.value = await obtenerSolicitudes()
  } catch (err) {
    error.value =
      err.message || 'No se pudieron cargar las solicitudes.'
  } finally {
    cargando.value = false
  }
}

// Limpiar formulario
function limpiarFormulario() {
  numero.value = ''
  observaciones.value = ''
  equiposSeleccionados.value = []
}

// Cancelar edición
function cancelarEdicion() {
  solicitudEditar.value = null
  limpiarFormulario()
}

// Cargar solicitud para editar
function editarSolicitud(solicitud) {
  if (!puedeGestionar.value) {
    return
  }

  if (solicitud.estado !== 'borrador') {
    error.value =
      'Solo se pueden editar solicitudes en borrador.'
    return
  }

  solicitudEditar.value = { ...solicitud }

  numero.value = solicitud.numero
  observaciones.value = solicitud.observaciones || ''

  equiposSeleccionados.value = (
    solicitud.equipos_asociados || []
  ).map((item) => String(item.equipo))

  error.value = ''
  mensaje.value = ''

  document
    .getElementById('formulario-solicitudes')
    ?.scrollIntoView({
      behavior: 'smooth',
      block: 'start',
    })
}

// Crear o actualizar solicitud
async function guardarSolicitud() {
  error.value = ''
  mensaje.value = ''

  if (!puedeGestionar.value) {
    error.value =
      'No tienes permisos para gestionar solicitudes.'
    return
  }

  if (!numero.value.trim()) {
    error.value = 'Introduce el número de solicitud.'
    return
  }

  if (equiposSeleccionados.value.length === 0) {
    error.value = 'Selecciona al menos un equipo.'
    return
  }

  const datos = {
    numero: numero.value.trim(),
    observaciones: observaciones.value.trim(),
    equipos: equiposSeleccionados.value.map(Number),
  }

  guardando.value = true

  try {
    if (modoEdicion.value) {
      await actualizarSolicitud(
        solicitudEditar.value.id,
        datos
      )

      mensaje.value =
        'Solicitud actualizada correctamente.'
    } else {
      await crearSolicitud(datos)

      mensaje.value =
        'Solicitud creada correctamente.'
    }

    cancelarEdicion()
    await cargarSolicitudes()
  } catch (err) {
    error.value =
      err.message || 'No se pudo guardar la solicitud.'
  } finally {
    guardando.value = false
  }
}

// Preparar revisión técnica
function editarRevision(item) {
  if (!puedeGestionar.value) {
    return
  }

  revisionEditando.value = item.id

  const revision = item.revision_tecnica

  condicionFisica.value =
    revision?.condicion_fisica || 'no_evaluada'

  diagnostico.value =
    revision?.diagnostico || ''

  observacionesTecnicas.value =
    revision?.observaciones || ''

  error.value = ''
  mensaje.value = ''
}

// Cancelar revisión técnica
function cancelarRevision() {
  revisionEditando.value = null

  condicionFisica.value = 'no_evaluada'
  diagnostico.value = ''
  observacionesTecnicas.value = ''
}

// Guardar revisión técnica
async function guardarRevisionTecnica(item) {
  error.value = ''
  mensaje.value = ''

  if (!puedeGestionar.value) {
    error.value =
      'No tienes permisos para registrar revisiones.'
    return
  }

  if (!diagnostico.value.trim()) {
    error.value =
      'El diagnóstico técnico es obligatorio.'
    return
  }

  guardandoRevision.value = true

  try {
    await guardarRevision(item.id, {
      condicion_fisica: condicionFisica.value,
      diagnostico: diagnostico.value.trim(),
      observaciones: observacionesTecnicas.value.trim(),
    })

    cancelarRevision()

    mensaje.value =
      'Revisión técnica guardada correctamente.'

    await cargarSolicitudes()

    // Se vuelve a montar el historial al abrirlo,
    // para consultar los eventos más recientes.
    historialAbierto.value = null
  } catch (err) {
    error.value =
      err.message || 'No se pudo guardar la revisión.'
  } finally {
    guardandoRevision.value = false
  }
}

// Mostrar u ocultar historial
function alternarHistorial(id) {
  historialAbierto.value =
    historialAbierto.value === id
      ? null
      : id
}

// Restablecer al cerrar sesión
function restablecerEstado() {
  solicitudes.value = []

  cancelarEdicion()
  cancelarRevision()

  historialAbierto.value = null

  error.value = ''
  mensaje.value = ''
}

// Detectar cambios de sesión
watch(
  () => props.sesion.autenticado,
  (autenticado) => {
    if (autenticado) {
      cargarSolicitudes()
    } else {
      restablecerEstado()
    }
  },
  { immediate: true }
)

// Detectar cambios de permisos
watch(
  () => props.sesion.puede_crear_equipos,
  (permitido) => {
    if (!permitido) {
      cancelarEdicion()
      cancelarRevision()
    }
  }
)
</script>

<template>
  <section class="solicitudes">
    <div class="titulo-seccion">
      <div>
        <h2>Solicitudes de baja</h2>

        <p>
          Gestión de solicitudes, equipos asociados,
          revisiones técnicas e historial de cambios.
        </p>
      </div>

      <span class="contador">
        {{ solicitudes.length }} solicitudes
      </span>
    </div>

    <p
      v-if="!sesion.autenticado"
      class="aviso"
    >
      Inicia sesión para consultar las solicitudes de baja.
    </p>

    <template v-else>
      <!-- FORMULARIO DE SOLICITUDES -->
      <div
        v-if="puedeGestionar"
        id="formulario-solicitudes"
        class="formulario"
      >
        <div class="cabecera">
          <h3>{{ tituloFormulario }}</h3>

          <span
            v-if="modoEdicion"
            class="etiqueta-edicion"
          >
            Modo edición
          </span>
        </div>

        <form @submit.prevent="guardarSolicitud">
          <fieldset :disabled="guardando">
            <div class="campo">
              <label for="numero-solicitud">
                Número de solicitud *
              </label>

              <input
                id="numero-solicitud"
                v-model="numero"
                type="text"
                maxlength="50"
                placeholder="Ejemplo: SOL-002"
                required
              />
            </div>

            <div class="campo">
              <label for="observaciones-solicitud">
                Observaciones
              </label>

              <textarea
                id="observaciones-solicitud"
                v-model="observaciones"
                rows="4"
                placeholder="Observaciones generales..."
              />
            </div>

            <fieldset class="seleccion-equipos">
              <legend>
                Equipos incluidos *
              </legend>

              <p class="ayuda">
                Selecciona los equipos que pertenecen
                a esta solicitud.
              </p>

              <label
                v-for="equipo in equipos"
                :key="equipo.id"
                class="opcion-equipo"
              >
                <input
                  v-model="equiposSeleccionados"
                  type="checkbox"
                  :value="String(equipo.id)"
                />

                <span>
                  <strong>
                    {{ equipo.no_inventario }}
                  </strong>

                  —
                  {{ equipo.tipo_recurso_nombre }}

                  <small v-if="equipo.marca">
                    ({{ equipo.marca }})
                  </small>
                </span>
              </label>

              <p v-if="equipos.length === 0">
                No hay equipos registrados.
              </p>
            </fieldset>

            <div class="acciones">
              <button
                type="submit"
                class="boton-principal"
              >
                {{
                  guardando
                    ? 'Guardando...'
                    : modoEdicion
                      ? 'Guardar cambios'
                      : 'Crear solicitud'
                }}
              </button>

              <button
                v-if="modoEdicion"
                type="button"
                class="boton-secundario"
                @click="cancelarEdicion"
              >
                Cancelar edición
              </button>
            </div>
          </fieldset>
        </form>
      </div>

      <!-- LISTADO DE SOLICITUDES -->
      <div class="listado">
        <div class="cabecera">
          <h3>Solicitudes registradas</h3>

          <button
            type="button"
            class="boton-secundario"
            :disabled="cargando"
            @click="cargarSolicitudes"
          >
            Actualizar lista
          </button>
        </div>

        <p v-if="cargando">
          Cargando solicitudes...
        </p>

        <p
          v-else-if="solicitudes.length === 0"
          class="sin-datos"
        >
          Todavía no hay solicitudes registradas.
        </p>

        <article
          v-for="solicitud in solicitudes"
          :key="solicitud.id"
          class="tarjeta"
        >
          <!-- DATOS GENERALES -->
          <div class="cabecera">
            <h4>
              {{ solicitud.numero }}
            </h4>

            <span
              class="estado"
              :class="{
                presentada:
                  solicitud.estado === 'presentada'
              }"
            >
              {{
                solicitud.estado === 'borrador'
                  ? 'Borrador'
                  : solicitud.estado
              }}
            </span>
          </div>

          <p>
            <strong>Solicitante:</strong>
            {{ solicitud.solicitante_nombre }}
          </p>

          <p>
            <strong>Fecha de creación:</strong>

            {{
              new Date(
                solicitud.fecha_creacion
              ).toLocaleString()
            }}
          </p>

          <p v-if="solicitud.observaciones">
            <strong>Observaciones:</strong>
            {{ solicitud.observaciones }}
          </p>

          <button
            v-if="
              puedeGestionar &&
              solicitud.estado === 'borrador'
            "
            type="button"
            class="boton-secundario"
            @click="editarSolicitud(solicitud)"
          >
            Editar solicitud
          </button>

          <!-- EQUIPOS ASOCIADOS -->
          <div class="equipos-asociados">
            <h4>
              Equipos asociados
            </h4>

            <p
              v-if="
                !solicitud.equipos_asociados ||
                solicitud.equipos_asociados.length === 0
              "
            >
              No hay equipos asociados.
            </p>

            <div
              v-for="item in solicitud.equipos_asociados"
              :key="item.id"
              class="equipo"
            >
              <div class="cabecera-equipo">
                <strong>
                  {{ item.no_inventario }}
                </strong>

                <span
                  v-if="item.revision_tecnica"
                  class="revision-completa"
                >
                  Revisado
                </span>

                <span
                  v-else
                  class="revision-pendiente"
                >
                  Sin revisión
                </span>
              </div>

              <!-- REVISIÓN REGISTRADA -->
              <template v-if="item.revision_tecnica">
                <p>
                  <strong>Condición física:</strong>
                  {{
                    item.revision_tecnica.condicion_fisica
                  }}
                </p>

                <p>
                  <strong>Diagnóstico:</strong>
                  {{
                    item.revision_tecnica.diagnostico
                  }}
                </p>

                <p
                  v-if="
                    item.revision_tecnica.observaciones
                  "
                >
                  <strong>Observaciones técnicas:</strong>
                  {{
                    item.revision_tecnica.observaciones
                  }}
                </p>

                <p>
                  <strong>Revisado por:</strong>
                  {{
                    item.revision_tecnica.revisor_nombre
                  }}
                </p>

                <p>
                  <strong>Última revisión:</strong>
                  {{
                    new Date(
                      item.revision_tecnica.fecha_revision
                    ).toLocaleString()
                  }}
                </p>
              </template>

              <p v-else class="pendiente">
                Este equipo todavía no tiene
                una revisión técnica registrada.
              </p>

              <!-- BOTÓN DE REVISIÓN -->
              <button
                v-if="
                  puedeGestionar &&
                  solicitud.estado === 'borrador'
                "
                type="button"
                class="boton-secundario"
                @click="editarRevision(item)"
              >
                {{
                  item.revision_tecnica
                    ? 'Editar revisión técnica'
                    : 'Registrar revisión técnica'
                }}
              </button>

              <!-- FORMULARIO DE REVISIÓN -->
              <form
                v-if="revisionEditando === item.id"
                class="formulario-revision"
                @submit.prevent="
                  guardarRevisionTecnica(item)
                "
              >
                <fieldset :disabled="guardandoRevision">
                  <h4>
                    Revisión técnica:
                    {{ item.no_inventario }}
                  </h4>

                  <div class="campo">
                    <label
                      :for="`condicion-${item.id}`"
                    >
                      Condición física
                    </label>

                    <select
                      :id="`condicion-${item.id}`"
                      v-model="condicionFisica"
                    >
                      <option value="no_evaluada">
                        No evaluada
                      </option>

                      <option value="buena">
                        Buena
                      </option>

                      <option value="regular">
                        Regular
                      </option>

                      <option value="mala">
                        Mala
                      </option>
                    </select>
                  </div>

                  <div class="campo">
                    <label
                      :for="`diagnostico-${item.id}`"
                    >
                      Diagnóstico técnico *
                    </label>

                    <textarea
                      :id="`diagnostico-${item.id}`"
                      v-model="diagnostico"
                      rows="4"
                      required
                      placeholder="Describe el diagnóstico..."
                    />
                  </div>

                  <div class="campo">
                    <label
                      :for="`observaciones-${item.id}`"
                    >
                      Observaciones técnicas
                    </label>

                    <textarea
                      :id="`observaciones-${item.id}`"
                      v-model="observacionesTecnicas"
                      rows="3"
                      placeholder="Observaciones adicionales..."
                    />
                  </div>

                  <div class="acciones">
                    <button
                      type="submit"
                      class="boton-principal"
                    >
                      {{
                        guardandoRevision
                          ? 'Guardando...'
                          : 'Guardar revisión'
                      }}
                    </button>

                    <button
                      type="button"
                      class="boton-secundario"
                      @click="cancelarRevision"
                    >
                      Cancelar
                    </button>
                  </div>
                </fieldset>
              </form>
            </div>
          </div>

          <!-- HISTORIAL DE LA SOLICITUD -->
          <div class="historial-contenedor">
            <button
              type="button"
              class="boton-historial"
              @click="
                alternarHistorial(solicitud.id)
              "
            >
              {{
                historialAbierto === solicitud.id
                  ? 'Ocultar historial'
                  : 'Ver historial de cambios'
              }}
            </button>

            <HistorialSolicitud
              v-if="
                historialAbierto === solicitud.id
              "
              :solicitud-id="solicitud.id"
            />
          </div>
        </article>
      </div>
    </template>

    <!-- MENSAJES -->
    <p
      v-if="mensaje"
      class="mensaje"
      role="status"
    >
      {{ mensaje }}
    </p>

    <p
      v-if="error"
      class="error"
      role="alert"
    >
      {{ error }}
    </p>
  </section>
</template>

<style scoped>
.solicitudes {
  margin-top: 36px;
  padding: 24px;
  border: 1px solid #d7e0e8;
  border-radius: 12px;
  background: white;
}

h2,
h3,
h4 {
  color: #123b5d;
}

.titulo-seccion,
.cabecera,
.cabecera-equipo {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.titulo-seccion {
  margin-bottom: 24px;
}

.contador {
  padding: 8px 12px;
  border-radius: 20px;
  background: #eaf1f7;
  color: #123b5d;
  white-space: nowrap;
  font-size: 13px;
}

.formulario {
  margin-top: 20px;
  padding: 20px;
  border: 1px solid #d7e0e8;
  border-radius: 10px;
  background: #f7f9fc;
  scroll-margin-top: 20px;
}

.etiqueta-edicion {
  padding: 6px 10px;
  background: #e3efff;
  color: #174b8c;
  border-radius: 20px;
  font-size: 12px;
}

fieldset {
  border: 0;
  padding: 0;
  margin: 0;
  min-width: 0;
}

.campo {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin: 18px 0;
}

.campo label {
  font-weight: 600;
}

.campo input,
.campo textarea,
.campo select {
  padding: 12px;
  border: 1px solid #ccd8e2;
  border-radius: 8px;
  font: inherit;
  background: white;
}

.seleccion-equipos {
  margin: 20px 0;
  padding: 16px;
  border: 1px solid #d7e0e8;
  border-radius: 8px;
  background: white;
}

.seleccion-equipos legend {
  font-weight: 600;
}

.ayuda {
  color: #536879;
  font-size: 14px;
}

.opcion-equipo {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  margin: 12px 0;
}

.opcion-equipo input {
  margin-top: 4px;
}

.acciones {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 16px;
}

button {
  padding: 10px 16px;
  border-radius: 8px;
  cursor: pointer;
  font: inherit;
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.boton-principal {
  border: none;
  background: #123b5d;
  color: white;
}

.boton-secundario {
  border: 1px solid #123b5d;
  background: white;
  color: #123b5d;
}

.listado {
  margin-top: 32px;
}

.sin-datos {
  padding: 24px;
  background: #f7f9fc;
  border-radius: 8px;
}

.tarjeta {
  margin-top: 16px;
  padding: 20px;
  border: 1px solid #d7e0e8;
  border-radius: 10px;
  background: #fff;
}

.tarjeta h4 {
  margin: 10px 0;
}

.estado {
  padding: 6px 10px;
  background: #eaf1f7;
  color: #123b5d;
  border-radius: 20px;
  font-size: 12px;
}

.estado.presentada {
  background: #e8f5e9;
  color: #226c38;
}

.equipos-asociados {
  margin-top: 24px;
}

.equipo {
  margin-top: 14px;
  padding: 18px;
  border: 1px solid #d7e0e8;
  border-radius: 10px;
  background: #f8fafc;
}

.revision-completa {
  padding: 5px 10px;
  background: #e8f5e9;
  color: #226c38;
  border-radius: 20px;
  font-size: 12px;
}

.revision-pendiente {
  padding: 5px 10px;
  background: #fff3df;
  color: #8a5b16;
  border-radius: 20px;
  font-size: 12px;
}

.pendiente {
  color: #8a5b16;
}

.formulario-revision {
  margin-top: 18px;
  padding: 18px;
  border: 1px solid #d7e0e8;
  border-radius: 8px;
  background: white;
}

.historial-contenedor {
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #d7e0e8;
}

.boton-historial {
  border: 1px solid #123b5d;
  background: #eaf1f7;
  color: #123b5d;
}

.aviso {
  color: #755014;
}

.mensaje {
  margin-top: 20px;
  padding: 12px;
  border-radius: 8px;
  background: #eaf7ee;
  color: #175c37;
}

.error {
  margin-top: 20px;
  padding: 12px;
  border-radius: 8px;
  background: #fff0ef;
  color: #b42318;
}

@media (max-width: 650px) {
  .solicitudes {
    padding: 14px;
  }

  .titulo-seccion,
  .cabecera {
    align-items: flex-start;
    flex-direction: column;
  }

  .formulario,
  .tarjeta {
    padding: 14px;
  }

  .contador {
    align-self: flex-start;
  }
}
</style>
