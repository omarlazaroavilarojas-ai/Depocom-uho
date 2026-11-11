
<script setup>
import { ref, computed, watch, onMounted } from "vue";

import {
  obtenerSolicitudes,
  presentarSolicitud,
  decidirSolicitudArea,
  iniciarRevisionTecnica,
  guardarRevisionTecnica,
  aprobarRevisionTecnica,
} from "../api/aprobaciones";

const props = defineProps({
  sesion: {
    type: Object,
    required: true,
  },
  modo: { type: String, default: "area" },
});

const solicitudes = ref([]);
const solicitudesVisibles = computed(() => solicitudes.value.filter(s =>
  props.modo === "revision"
    ? ["aprobada_area", "en_revision", "aprobada_tecnica"].includes(s.estado)
    : ["borrador", "presentada", "aprobada_area", "rechazada_area"].includes(s.estado)
));
const cargando = ref(false);
const procesando = ref(false);
const error = ref("");
const mensaje = ref("");
const comentarios = ref({});
const diagnosticos = ref({});

const roles = computed(() => {
  const valores = props.sesion?.roles || [];
  return Array.isArray(valores) ? valores : [];
});

function tieneRol(rol) {
  return roles.value.includes(rol);
}

const administrador = computed(() =>
  tieneRol("Administrador del Sistema")
);

const jefeDepartamento = computed(() =>
  tieneRol("Jefe de Departamento")
);

const jefeArea = computed(() =>
  tieneRol("Jefe de Área")
);

const tecnicoSoporte = computed(() =>
  tieneRol("Técnico de Soporte")
);

const jefeSoporte = computed(() =>
  tieneRol("Jefe de Soporte Técnico")
);

function puedePresentar(solicitud) {
  return (
    (administrador.value || jefeDepartamento.value) &&
    solicitud.estado === "borrador"
  );
}

function puedeDecidir(solicitud) {
  return (
    (administrador.value || jefeArea.value) &&
    solicitud.estado === "presentada"
  );
}

function puedeIniciarRevision(solicitud) {
  return (
    (administrador.value || tecnicoSoporte.value) &&
    solicitud.estado === "aprobada_area"
  );
}

function puedeRevisar(solicitud) {
  return (
    (administrador.value || tecnicoSoporte.value) &&
    solicitud.estado === "en_revision"
  );
}

function puedeAprobarRevision(solicitud) {
  return (
    (administrador.value || jefeSoporte.value) &&
    solicitud.estado === "en_revision"
  );
}

function etiquetaEstado(estado) {
  const etiquetas = {
    borrador: "Borrador",
    presentada: "Presentada",
    aprobada_area: "Aprobada por Área",
    rechazada_area: "Rechazada por Área",
    en_revision: "En Revisión Técnica",
    aprobada_tecnica: "Aprobada Técnicamente",
    pendiente_economia: "Pendiente de Economía",
    proceso_economico: "En Proceso Económico",
    aprobada_economia: "Aprobada por Economía",
    recibida_deposito: "Recibida en Depósito",
  };

  return etiquetas[estado] || estado || "Sin estado";
}

function obtenerEquipos(solicitud) {
  return Array.isArray(solicitud.equipos_asociados)
    ? solicitud.equipos_asociados
    : [];
}

function actualizarDiagnostico(equipoId, campo, valor) {
  diagnosticos.value[equipoId] = {
    ...(diagnosticos.value[equipoId] || {}),
    [campo]: valor,
  };
}

function obtenerDiagnostico(equipoId, campo) {
  return diagnosticos.value[equipoId]?.[campo] || "";
}

async function cargarSolicitudes() {
  cargando.value = true;
  error.value = "";

  try {
    solicitudes.value = await obtenerSolicitudes();
  } catch (e) {
    error.value =
      e.message || "No se pudieron cargar las solicitudes.";
  } finally {
    cargando.value = false;
  }
}

async function ejecutar(operacion, confirmacion) {
  if (procesando.value) return;

  procesando.value = true;
  error.value = "";
  mensaje.value = "";

  try {
    await operacion();
    mensaje.value = confirmacion;
    await cargarSolicitudes();
  } catch (e) {
    error.value =
      e.message || "Ocurrió un error al procesar la operación.";
  } finally {
    procesando.value = false;
  }
}

function presentar(solicitud) {
  ejecutar(
    () => presentarSolicitud(solicitud.id),
    "Solicitud presentada correctamente."
  );
}

function decidir(solicitud, decision) {
  const comentario = comentarios.value[solicitud.id] || "";

  if (decision === "rechazar" && !comentario.trim()) {
    error.value = "Debes indicar el motivo del rechazo.";
    return;
  }

  ejecutar(
    () =>
      decidirSolicitudArea(
        solicitud.id,
        decision,
        comentario
      ),
    "Decisión del área registrada correctamente."
  );
}

function iniciarRevision(solicitud) {
  ejecutar(
    () => iniciarRevisionTecnica(solicitud.id),
    "Revisión técnica iniciada correctamente."
  );
}

function guardarDiagnostico(equipo) {
  const datos = diagnosticos.value[equipo.id] || {};

  if (
    !datos.condicion_fisica ||
    datos.condicion_fisica === "no_evaluada"
  ) {
    error.value =
      "Debes seleccionar una condición física válida.";
    return;
  }

  if (!datos.diagnostico?.trim()) {
    error.value = "Debes escribir el diagnóstico técnico.";
    return;
  }

  ejecutar(
    () =>
      guardarRevisionTecnica(equipo.id, {
        condicion_fisica: datos.condicion_fisica,
        diagnostico: datos.diagnostico.trim(),
        observaciones: datos.observaciones || "",
      }),
    "Diagnóstico técnico guardado correctamente."
  );
}

function aprobarRevision(solicitud) {
  ejecutar(
    () => aprobarRevisionTecnica(solicitud.id),
    "Revisión técnica aprobada correctamente."
  );
}

watch(
  () => props.sesion?.autenticado,
  (autenticado) => {
    if (autenticado) {
      cargarSolicitudes();
    } else {
      solicitudes.value = [];
      diagnosticos.value = {};
      comentarios.value = {};
    }
  }
);

onMounted(() => {
  if (props.sesion?.autenticado) {
    cargarSolicitudes();
  }
});
</script>

<template>
  <section class="panel-aprobaciones">
    <header class="cabecera">
      <div>
        <h2>{{ modo === "revision" ? "Revisión técnica" : "Aprobación de área" }}</h2>
        <p>{{ modo === "revision" ? "Diagnóstico de equipos y aprobación técnica" : "Presentación y decisión de solicitudes de baja" }}</p>
      </div>

      <button
        type="button"
        :disabled="cargando || procesando"
        @click="cargarSolicitudes"
      >
        Actualizar
      </button>
    </header>

    <p v-if="error" class="alerta error">
      {{ error }}
    </p>

    <p v-if="mensaje" class="alerta exito">
      {{ mensaje }}
    </p>

    <p v-if="cargando">
      Cargando solicitudes...
    </p>

    <p v-else-if="!solicitudesVisibles.length">
      No hay solicitudes disponibles para tu usuario.
    </p>

    <div v-else class="lista">
      <article
        v-for="solicitud in solicitudesVisibles"
        :key="solicitud.id"
        class="solicitud"
      >
        <div class="fila">
          <div>
            <h3>Solicitud {{ solicitud.numero || solicitud.id }}</h3>
            <p><strong>Departamento:</strong> {{ solicitud.departamento_nombre || solicitud.departamento?.nombre || solicitud.departamento || "Sin asignar" }}</p>

            <span class="estado">
              {{ etiquetaEstado(solicitud.estado) }}
            </span>
          </div>

          <button
            v-if="modo === 'area' && puedePresentar(solicitud)"
            type="button"
            :disabled="procesando"
            @click="presentar(solicitud)"
          >
            Presentar solicitud
          </button>
        </div>

        <div
          v-if="modo === 'area' && puedeDecidir(solicitud)"
          class="acciones"
        >
          <h4>Decisión del jefe de área</h4>

          <label>
            Comentario
            <textarea
              v-model="comentarios[solicitud.id]"
              placeholder="Observaciones o motivo del rechazo"
              rows="2"
            ></textarea>
          </label>

          <div class="botones">
            <button
              type="button"
              :disabled="procesando"
              @click="decidir(solicitud, 'aprobar')"
            >
              Aprobar solicitud
            </button>

            <button
              type="button"
              class="peligro"
              :disabled="procesando"
              @click="decidir(solicitud, 'rechazar')"
            >
              Rechazar solicitud
            </button>
          </div>
        </div>

        <div
          v-if="modo === 'revision' && puedeIniciarRevision(solicitud)"
          class="acciones"
        >
          <h4>Revisión técnica</h4>

          <button
            type="button"
            :disabled="procesando"
            @click="iniciarRevision(solicitud)"
          >
            Iniciar revisión técnica
          </button>
        </div>

        <div
          v-if="modo === 'revision' && puedeRevisar(solicitud)"
          class="acciones"
        >
          <h4>Diagnóstico de equipos</h4>

          <p v-if="!obtenerEquipos(solicitud).length">
            No se recibieron los equipos asociados.
            Comprueba que la API incluya equipos_asociados.
          </p>

          <div
            v-for="equipo in obtenerEquipos(solicitud)"
            :key="equipo.id"
            class="equipo"
          >
            <strong>
              Equipo #{{ equipo.id }}
            </strong>

            <label>
              Condición física

              <select
                :value="
                  obtenerDiagnostico(
                    equipo.id,
                    'condicion_fisica'
                  )
                "
                @change="
                  actualizarDiagnostico(
                    equipo.id,
                    'condicion_fisica',
                    $event.target.value
                  )
                "
              >
                <option value="">
                  Seleccionar
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
            </label>

            <label>
              Diagnóstico técnico

              <textarea
                :value="
                  obtenerDiagnostico(
                    equipo.id,
                    'diagnostico'
                  )
                "
                @input="
                  actualizarDiagnostico(
                    equipo.id,
                    'diagnostico',
                    $event.target.value
                  )
                "
                placeholder="Describe el estado del equipo"
                rows="3"
              ></textarea>
            </label>

            <label>
              Observaciones

              <textarea
                :value="
                  obtenerDiagnostico(
                    equipo.id,
                    'observaciones'
                  )
                "
                @input="
                  actualizarDiagnostico(
                    equipo.id,
                    'observaciones',
                    $event.target.value
                  )
                "
                placeholder="Observaciones adicionales"
                rows="2"
              ></textarea>
            </label>

            <button
              type="button"
              :disabled="procesando"
              @click="guardarDiagnostico(equipo)"
            >
              Guardar diagnóstico
            </button>
          </div>
        </div>

        <div
          v-if="modo === 'revision' && puedeAprobarRevision(solicitud)"
          class="acciones"
        >
          <h4>Aprobación del jefe de soporte</h4>

          <p>
            Todos los equipos deben estar evaluados
            antes de aprobar la revisión técnica.
          </p>

          <button
            type="button"
            :disabled="procesando"
            @click="aprobarRevision(solicitud)"
          >
            Aprobar revisión técnica
          </button>
        </div>
      </article>
    </div>
  </section>
</template>

<style scoped>
.panel-aprobaciones {
  padding: 20px;
  color: #1f2937;
}

.cabecera,
.fila,
.botones {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.cabecera {
  margin-bottom: 20px;
}

.cabecera h2 {
  margin: 0;
}

.cabecera p {
  color: #64748b;
}

.lista {
  display: grid;
  gap: 16px;
}

.solicitud,
.equipo {
  padding: 16px;
  border: 1px solid #dbe2ea;
  border-radius: 10px;
  background: #ffffff;
}

.solicitud h3 {
  margin: 0;
}

.estado {
  display: inline-block;
  margin-top: 8px;
  padding: 5px 10px;
  background: #e2e8f0;
  border-radius: 20px;
  font-size: 13px;
}

.acciones {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #e2e8f0;
}

.equipo {
  margin-top: 12px;
}

label {
  display: grid;
  gap: 6px;
  margin: 10px 0;
}

textarea,
select {
  width: 100%;
  padding: 10px;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  box-sizing: border-box;
  font: inherit;
}

button {
  padding: 10px 14px;
  border: 0;
  border-radius: 6px;
  background: #2563eb;
  color: white;
  cursor: pointer;
}

button:hover:not(:disabled) {
  background: #1d4ed8;
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.peligro {
  background: #dc2626;
}

.peligro:hover:not(:disabled) {
  background: #b91c1c;
}

.alerta {
  padding: 12px;
  margin-bottom: 16px;
  border-radius: 6px;
}

.error {
  background: #fee2e2;
  color: #991b1b;
}

.exito {
  background: #dcfce7;
  color: #166534;
}
</style>
