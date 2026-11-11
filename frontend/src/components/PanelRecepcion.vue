<script setup>
import { computed, ref, watch, onMounted } from 'vue'
import { listarSolicitudesRecepcion, consultarRecepcion, recibirEquipo } from '../api/recepcion'

const props = defineProps({ sesion: { type: Object, required: true } })
const roles = computed(() => props.sesion?.roles || [])
const puedeRecibir = computed(() => roles.value.some(r => ['Administrador del Sistema', 'Jefe de Soporte Técnico', 'Técnico de Soporte'].includes(r)))
const visible = computed(() => !!props.sesion?.autenticado)
const solicitudes = ref([])
const seleccionada = ref('')
const detalle = ref(null)
const observaciones = ref({})
const cargando = ref(false)
const consultando = ref(false)
const guardando = ref(null)
const error = ref('')
const aviso = ref('')
const elegibles = computed(() => solicitudes.value.filter(s => ['aprobada_economia', 'recibida_deposito'].includes(s.estado)))

async function cargar() {
  if (!visible.value) { solicitudes.value = []; detalle.value = null; seleccionada.value = ''; return }
  cargando.value = true; error.value = ''
  try {
    const datos = await listarSolicitudesRecepcion()
    solicitudes.value = Array.isArray(datos) ? datos : (datos.results || [])
    if (seleccionada.value && !elegibles.value.some(s => String(s.id) === String(seleccionada.value))) {
      seleccionada.value = ''; detalle.value = null
    }
  } catch (e) { error.value = e.message || 'No se pudieron consultar las solicitudes.' }
  finally { cargando.value = false }
}
async function verDetalle() {
  detalle.value = null
  if (!seleccionada.value) return
  consultando.value = true; error.value = ''; aviso.value = ''
  try { detalle.value = await consultarRecepcion(seleccionada.value) }
  catch (e) { error.value = e.message || 'No se pudo consultar la recepción.' }
  finally { consultando.value = false }
}
async function registrar(equipo) {
  if (!puedeRecibir.value || guardando.value !== null || !detalle.value || equipo.recibido) return
  if (!window.confirm(`¿Confirmas la recepción del equipo ${equipo.no_inventario}?`)) return
  guardando.value = equipo.equipo_solicitud_id; error.value = ''; aviso.value = ''
  try {
    detalle.value = await recibirEquipo(seleccionada.value, equipo.equipo_solicitud_id, observaciones.value[equipo.equipo_solicitud_id] || '')
    observaciones.value[equipo.equipo_solicitud_id] = ''
    aviso.value = detalle.value.pendientes === 0 ? 'Todos los equipos de la solicitud fueron recibidos.' : 'Equipo recibido correctamente.'
    await cargar()
  } catch (e) { error.value = e.message || 'No se pudo registrar la recepción.' }
  finally { guardando.value = null }
}
watch(() => [props.sesion?.autenticado, ...(props.sesion?.roles || [])], cargar)
onMounted(cargar)
</script>

<template>
  <section v-if="visible" class="recepcion">
    <header class="cabecera">
      <div>
        <span class="eyebrow">DEPÓSITO · CONTROL DE ENTRADAS</span>
        <h2>Recepción de equipos</h2>
        <p>Verifica los equipos aprobados y registra su llegada física al depósito.</p>
      </div>
      <button type="button" class="secundario" :disabled="cargando || guardando !== null" @click="cargar">Actualizar solicitudes</button>
    </header>

    <p v-if="error" class="mensaje error" role="alert">{{ error }}</p>
    <p v-if="aviso" class="mensaje exito" role="status">{{ aviso }}</p>

    <div class="selector">
      <label for="recepcion-solicitud">Solicitud aprobada económicamente</label>
      <div class="selector-fila">
        <select id="recepcion-solicitud" v-model="seleccionada" :disabled="cargando || guardando !== null" @change="verDetalle">
          <option value="">Selecciona una solicitud…</option>
          <option v-for="s in elegibles" :key="s.id" :value="String(s.id)">{{ s.numero }} · {{ s.estado === 'recibida_deposito' ? 'Recepción completa' : 'Pendiente de recepción' }}</option>
        </select>
        <button type="button" class="secundario" :disabled="!seleccionada || consultando" @click="verDetalle">Consultar</button>
      </div>
      <p v-if="cargando" class="ayuda">Cargando solicitudes…</p>
      <p v-else-if="elegibles.length === 0" class="ayuda">No hay solicitudes aprobadas económicamente disponibles para recepción.</p>
    </div>

    <p v-if="consultando" class="ayuda">Consultando equipos…</p>
    <template v-if="detalle">
      <div class="resumen">
        <div class="indicador"><span>Total de equipos</span><strong>{{ detalle.total }}</strong></div>
        <div class="indicador"><span>Recibidos</span><strong>{{ detalle.recibidos }}</strong></div>
        <div class="indicador"><span>Pendientes</span><strong>{{ detalle.pendientes }}</strong></div>
      </div>
      <div class="progreso" role="progressbar" :aria-valuenow="detalle.recibidos" :aria-valuemin="0" :aria-valuemax="detalle.total || 1" aria-label="Equipos recibidos">
        <div :style="{ width: (detalle.total ? detalle.recibidos / detalle.total * 100 : 0) + '%' }"></div>
      </div>
      <p v-if="detalle.pendientes === 0" class="mensaje exito">Recepción completa. No quedan equipos pendientes.</p>
      <p v-if="!puedeRecibir" class="mensaje informativo">Tu usuario puede consultar las recepciones, pero no registrarlas.</p>
      <div class="lista">
        <article v-for="equipo in detalle.equipos" :key="equipo.equipo_solicitud_id" class="equipo">
          <div class="equipo-info">
            <div><strong>{{ equipo.no_inventario }}</strong><small>Equipo #{{ equipo.equipo_id }}</small></div>
            <span :class="['etiqueta', equipo.recibido ? 'recibido' : 'pendiente']">{{ equipo.recibido ? 'Recibido' : 'Pendiente' }}</span>
          </div>
          <div v-if="!equipo.recibido && puedeRecibir" class="acciones">
            <label :for="`observaciones-${equipo.equipo_solicitud_id}`">Observaciones (opcional)</label>
            <textarea :id="`observaciones-${equipo.equipo_solicitud_id}`" v-model="observaciones[equipo.equipo_solicitud_id]" maxlength="2000" rows="2" placeholder="Estado del equipo al llegar, incidencias…"></textarea>
            <button type="button" :disabled="guardando !== null" @click="registrar(equipo)">{{ guardando === equipo.equipo_solicitud_id ? 'Registrando…' : 'Confirmar recepción' }}</button>
          </div>
        </article>
      </div>
    </template>
  </section>
</template>

<style scoped>
.recepcion{margin-top:28px;padding:28px;background:#fff;border:1px solid #e2e8f0;border-radius:18px;box-shadow:0 6px 24px #0f172a0b;color:#172b4d}
.cabecera{display:flex;justify-content:space-between;align-items:flex-start;gap:20px;flex-wrap:wrap}.cabecera h2{margin:6px 0 8px;font-size:25px}.cabecera p{margin:0;color:#64748b}.eyebrow{font-size:11px;font-weight:800;letter-spacing:1.4px;color:#2563eb}
button{background:#1457b8;border:1px solid #1457b8;color:white;border-radius:9px;padding:10px 15px;font-weight:700;cursor:pointer}button:disabled{opacity:.5;cursor:not-allowed}.secundario{background:white;color:#1457b8;border-color:#bfdbfe}
.selector{margin-top:26px;padding:18px;border-radius:12px;background:#f8fafc;border:1px solid #e2e8f0}.selector label,.acciones label{display:block;font-weight:650;font-size:13px;margin-bottom:9px}.selector-fila{display:flex;gap:10px}.selector select{min-width:0;flex:1;padding:11px;border:1px solid #cbd5e1;border-radius:9px;background:white;color:#1e293b}.ayuda{color:#64748b;font-size:14px}
.resumen{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:20px}.indicador{border:1px solid #e2e8f0;border-radius:12px;padding:17px}.indicador span{display:block;font-size:12px;color:#64748b}.indicador strong{display:block;font-size:28px;margin-top:5px}.progreso{height:9px;border-radius:20px;background:#e2e8f0;overflow:hidden;margin:17px 0}.progreso>div{height:100%;background:#16a34a;transition:width .2s}
.lista{display:grid;gap:12px;margin-top:17px}.equipo{border:1px solid #e2e8f0;border-radius:12px;padding:17px}.equipo-info{display:flex;justify-content:space-between;align-items:center;gap:10px}.equipo-info small{display:block;color:#64748b;margin-top:4px}.etiqueta{font-size:12px;font-weight:700;border-radius:20px;padding:5px 10px}.recibido{background:#dcfce7;color:#166534}.pendiente{background:#fef3c7;color:#92400e}.acciones{margin-top:16px}.acciones textarea{display:block;width:100%;box-sizing:border-box;padding:10px;border:1px solid #cbd5e1;border-radius:8px;resize:vertical;font:inherit;margin-bottom:12px}.mensaje{padding:12px 15px;border-radius:9px;margin-top:16px}.error{background:#fef2f2;color:#991b1b}.exito{background:#f0fdf4;color:#166534}.informativo{background:#eff6ff;color:#1e40af}
@media(max-width:650px){.recepcion{padding:17px}.resumen{gap:7px}.indicador{padding:11px}.indicador strong{font-size:22px}.selector-fila{flex-direction:column}}
</style>
