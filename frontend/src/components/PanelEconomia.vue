<script setup>
import { computed, onMounted, ref, watch } from 'vue';
import { listarSolicitudesEconomia, ejecutarAccionEconomica } from '../api/economia';

const props = defineProps({ sesion: { type: Object, required: true } });
const solicitudes = ref([]);
const cargando = ref(false);
const procesandoId = ref(null);
const error = ref('');
const aviso = ref('');
const comentarios = ref({});
const estados = {
  aprobada_tecnica: 'Aprobada técnicamente',
  pendiente_economia: 'Pendiente de Economía',
  proceso_economico: 'En proceso económico',
  aprobada_economia: 'Aprobada por Economía',
};
const roles = computed(() => props.sesion?.roles || []);
const admin = computed(() => roles.value.includes('Administrador del Sistema'));
const soporte = computed(() => admin.value || roles.value.includes('Jefe de Soporte Técnico'));
const economia = computed(() => admin.value || roles.value.includes('Jefe de Economía'));
const habilitado = computed(() => Boolean(props.sesion?.autenticado) && (soporte.value || economia.value));
const relevantes = computed(() => solicitudes.value.filter((s) => Object.hasOwn(estados, s.estado)));

async function cargar() {
  if (!habilitado.value) { solicitudes.value = []; return; }
  cargando.value = true;
  error.value = '';
  try {
    const data = await listarSolicitudesEconomia();
    solicitudes.value = Array.isArray(data) ? data : (data.results || []);
  } catch (e) { error.value = e.message || 'No fue posible cargar las solicitudes.'; }
  finally { cargando.value = false; }
}

function accionDisponible(s) {
  if (s.estado === 'aprobada_tecnica' && soporte.value) return { clave: 'remitir', etiqueta: 'Remitir a Economía' };
  if (s.estado === 'pendiente_economia' && economia.value) return { clave: 'iniciar', etiqueta: 'Iniciar proceso económico' };
  if (s.estado === 'proceso_economico' && economia.value) return { clave: 'aprobar', etiqueta: 'Aprobar económicamente' };
  return null;
}

async function ejecutar(s) {
  const accion = accionDisponible(s);
  if (!accion || procesandoId.value !== null) return;
  if (!window.confirm(`¿Confirmas: ${accion.etiqueta.toLowerCase()} para ${s.numero}?`)) return;
  procesandoId.value = s.id;
  aviso.value = '';
  error.value = '';
  try {
    const data = await ejecutarAccionEconomica(s.id, accion.clave, comentarios.value[s.id] || '');
    aviso.value = data.mensaje || 'Operación realizada correctamente.';
    comentarios.value[s.id] = '';
    await cargar();
  } catch (e) { error.value = e.message || 'No se pudo completar la operación.'; }
  finally { procesandoId.value = null; }
}

watch(() => [props.sesion?.autenticado, ...(props.sesion?.roles || [])], cargar);
onMounted(cargar);
</script>

<template>
  <section v-if="habilitado" class="economia-panel">
    <header class="economia-header">
      <div>
        <h2>Gestión económica de bajas</h2>
        <p>Remisión, tramitación y aprobación económica de solicitudes.</p>
      </div>
      <button type="button" :disabled="cargando" @click="cargar">Actualizar</button>
    </header>
    <p v-if="error" class="economia-error" role="alert">{{ error }}</p>
    <p v-if="aviso" class="economia-ok" role="status">{{ aviso }}</p>
    <p v-if="cargando">Cargando solicitudes…</p>
    <p v-else-if="relevantes.length === 0">No hay solicitudes en el circuito económico.</p>
    <div v-else class="economia-lista">
      <article v-for="s in relevantes" :key="s.id" class="economia-tarjeta">
        <div class="economia-datos">
          <h3>Solicitud {{ s.numero }}</h3>
          <span class="economia-estado">{{ estados[s.estado] }}</span>
        </div>
        <p><strong>Solicitante:</strong> {{ s.solicitante_nombre || 'Sin información' }}</p>
        <p v-if="s.observaciones"><strong>Observaciones:</strong> {{ s.observaciones }}</p>
        <p><strong>Equipos asociados:</strong> {{ (s.equipos_asociados || []).length }}</p>
        <ul v-if="s.equipos_asociados?.length">
          <li v-for="e in s.equipos_asociados" :key="e.id">Inventario: {{ e.no_inventario || e.equipo }}</li>
        </ul>
        <template v-if="accionDisponible(s)">
          <label :for="`economia-comentario-${s.id}`">Comentario (opcional)</label>
          <textarea :id="`economia-comentario-${s.id}`" v-model="comentarios[s.id]" maxlength="2000" rows="2" placeholder="Observaciones de la decisión"></textarea>
          <button type="button" :disabled="procesandoId !== null" @click="ejecutar(s)">
            {{ procesandoId === s.id ? 'Procesando…' : accionDisponible(s).etiqueta }}
          </button>
        </template>
      </article>
    </div>
  </section>
</template>

<style scoped>
.economia-panel{margin:1.5rem 0;padding:1.25rem;border:1px solid #d9dee5;border-radius:12px;background:#fff;color:#1e293b}
.economia-header,.economia-datos{display:flex;justify-content:space-between;align-items:center;gap:1rem;flex-wrap:wrap}
h2,h3{margin:0 0 .4rem}p{margin:.45rem 0}.economia-header{margin-bottom:1.2rem}.economia-header p{color:#64748b}
.economia-lista{display:grid;gap:1rem}.economia-tarjeta{padding:1rem;border:1px solid #e2e8f0;border-radius:10px}
.economia-estado{background:#e8eef8;border-radius:16px;padding:.3rem .7rem;font-size:.85rem}
label{display:block;margin:.75rem 0 .3rem;font-weight:600}textarea{box-sizing:border-box;display:block;width:100%;padding:.65rem;border:1px solid #cbd5e1;border-radius:7px;font:inherit}
button{margin-top:.6rem;padding:.6rem 1rem;border:0;border-radius:7px;background:#1d4ed8;color:#fff;cursor:pointer}button:disabled{opacity:.55;cursor:not-allowed}
.economia-error{color:#b91c1c}.economia-ok{color:#166534}
</style>
