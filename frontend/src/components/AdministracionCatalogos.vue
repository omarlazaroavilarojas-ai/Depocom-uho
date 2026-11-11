<script setup>
import { computed, onMounted, ref } from 'vue'

const props = defineProps({ sesion: { type: Object, default: () => ({}) } })
const puedeEditar = computed(() => Boolean(props.sesion?.permisos?.administrar))
const catalogos = [
  { id: 'sedes', nombre: 'Sedes', ruta: '/api/sedes/' },
  { id: 'areas', nombre: 'Áreas', ruta: '/api/areas/' },
  { id: 'departamentos', nombre: 'Departamentos', ruta: '/api/departamentos/' },
  { id: 'tipos', nombre: 'Tipos de recursos', ruta: '/api/tipos-recursos/' },
]
const actual = ref('sedes')
const registros = ref([])
const sedes = ref([])
const areas = ref([])
const busqueda = ref('')
const cargando = ref(false)
const guardando = ref(false)
const error = ref('')
const mensaje = ref('')
const editando = ref(null)
const formulario = ref({})
const abierto = ref(false)

const catalogo = computed(() => catalogos.find(c => c.id === actual.value))
const filtrados = computed(() => {
  const q = busqueda.value.toLocaleLowerCase().trim()
  return registros.value.filter(x => !q || JSON.stringify(x).toLocaleLowerCase().includes(q))
})
function csrfToken() {
  return decodeURIComponent(document.cookie.split('; ').find(c => c.startsWith('csrftoken='))?.split('=')[1] || '')
}
async function api(ruta, opciones = {}) {
  const respuesta = await fetch(ruta, { credentials: 'include', ...opciones })
  const datos = await respuesta.json().catch(() => ({}))
  if (!respuesta.ok) {
    const detalle = datos.detail || datos.error || Object.entries(datos).map(([k,v]) => `${k}: ${Array.isArray(v) ? v.join(', ') : v}`).join('; ')
    throw new Error(detalle || `Error HTTP ${respuesta.status}`)
  }
  return datos
}
function arreglo(x) { return Array.isArray(x) ? x : (x?.results || []) }
async function cargar() {
  cargando.value = true; error.value = ''; mensaje.value = ''
  try {
    const [lista, listaSedes, listaAreas] = await Promise.all([
      api(catalogo.value.ruta),
      api('/api/sedes/'),
      api('/api/areas/')
    ])
    registros.value = arreglo(lista)
    sedes.value = arreglo(listaSedes)
    areas.value = arreglo(listaAreas)
  } catch(e) { error.value = e.message; registros.value = [] }
  finally { cargando.value = false }
}
function cambiar(id) { actual.value = id; busqueda.value = ''; abierto.value = false; cargar() }
function nuevo() {
  editando.value = null
  formulario.value = actual.value === 'sedes' ? {nombre:'',direccion:''}
    : actual.value === 'areas' ? {nombre:'',descripcion:'',sede:''}
    : actual.value === 'departamentos' ? {nombre:'',tipo:'departamento',area:'',centro_costo:''}
    : {nombre:''}
  abierto.value = true; error.value = ''; mensaje.value = ''
}
function editar(registro) {
  editando.value = registro.id
  formulario.value = { ...registro }
  abierto.value = true; error.value = ''; mensaje.value = ''
}
async function guardar() {
  if (!puedeEditar.value || guardando.value) return
  guardando.value = true; error.value = ''; mensaje.value = ''
  try {
    await api('/api/csrf/')
    const ruta = editando.value ? `${catalogo.value.ruta}${editando.value}/` : catalogo.value.ruta
    const payload = { ...formulario.value }
    delete payload.id; delete payload.area_nombre; delete payload.sede_nombre
    await api(ruta, {
      method: editando.value ? 'PATCH' : 'POST',
      headers: {'Content-Type':'application/json','X-CSRFToken':csrfToken()},
      body: JSON.stringify(payload)
    })
    abierto.value = false
    await cargar()
    mensaje.value = editando.value ? 'Registro actualizado correctamente.' : 'Registro creado correctamente.'
  } catch(e) { error.value = e.message }
  finally { guardando.value = false }
}
onMounted(cargar)
</script>

<template>
  <section class="panel">
    <div class="panel-title"><h3>Administración de catálogos</h3><span>{{ puedeEditar ? 'ADMINISTRADOR' : 'SOLO CONSULTA' }}</span></div>
    <p>Gestiona los catálogos institucionales desde DepoCom UHO. Las relaciones entre sedes, áreas y departamentos se mantienen en el backend.</p>
    <div class="catalog-tabs">
      <button v-for="c in catalogos" :key="c.id" type="button" class="secondary"
        :class="{ elegido: actual === c.id }" @click="cambiar(c.id)">{{ c.nombre }}</button>
    </div>
    <div class="catalog-toolbar">
      <input v-model="busqueda" aria-label="Buscar registros" placeholder="Buscar en este catálogo…" />
      <button type="button" class="secondary" @click="cargar" :disabled="cargando">Actualizar</button>
      <button v-if="puedeEditar" type="button" class="primary" @click="nuevo">+ Nuevo registro</button>
    </div>
    <p v-if="error" class="form-error" role="alert">{{ error }}</p>
    <p v-if="mensaje" class="catalog-success" role="status">{{ mensaje }}</p>
    <p v-if="cargando">Cargando registros…</p>
    <p v-else-if="!filtrados.length">No hay registros que coincidan con la búsqueda.</p>
    <div v-else class="table-scroll">
      <table>
        <thead><tr><th>ID</th><th>Nombre</th><th v-if="actual==='sedes'">Dirección</th><th v-if="actual==='areas'">Sede</th><th v-if="actual==='departamentos'">Área / Sede</th><th v-if="puedeEditar">Acciones</th></tr></thead>
        <tbody>
          <tr v-for="registro in filtrados" :key="registro.id">
            <td>{{ registro.id }}</td><td>{{ registro.nombre }}</td>
            <td v-if="actual==='sedes'">{{ registro.direccion }}</td>
            <td v-if="actual==='areas'">{{ registro.sede_nombre }}</td>
            <td v-if="actual==='departamentos'">{{ registro.area_nombre }} / {{ registro.sede_nombre }}</td>
            <td v-if="puedeEditar"><button type="button" class="secondary" @click="editar(registro)">Editar</button></td>
          </tr>
        </tbody>
      </table>
    </div>

    <form v-if="abierto && puedeEditar" class="catalog-form" @submit.prevent="guardar">
      <div class="panel-title"><h3>{{ editando ? 'Editar' : 'Crear' }} {{ catalogo.nombre.toLowerCase() }}</h3><button type="button" class="secondary" @click="abierto=false">Cerrar</button></div>
      <label>Nombre <input v-model.trim="formulario.nombre" required maxlength="150" /></label>
      <label v-if="actual==='sedes'">Dirección <input v-model.trim="formulario.direccion" required maxlength="255" /></label>
      <label v-if="actual==='areas'">Descripción <textarea v-model="formulario.descripcion" rows="2" /></label>
      <label v-if="actual==='areas'">Sede
        <select v-model="formulario.sede" required><option disabled value="">Selecciona una sede</option><option v-for="s in sedes" :key="s.id" :value="s.id">{{ s.nombre }}</option></select>
      </label>
      <template v-if="actual==='departamentos'">
        <label>Tipo
          <select v-model="formulario.tipo" required>
            <option value="departamento">Departamento</option><option value="direccion">Dirección</option><option value="grupo">Grupo</option>
          </select>
        </label>
        <label>Área
          <select v-model="formulario.area" required><option disabled value="">Selecciona un área</option><option v-for="a in areas" :key="a.id" :value="a.id">{{ a.nombre }} — {{ a.sede_nombre }}</option></select>
        </label>
        <label>Centro de costo <input v-model.trim="formulario.centro_costo" maxlength="100" /></label>
      </template>
      <button class="primary" type="submit" :disabled="guardando">{{ guardando ? 'Guardando…' : 'Guardar' }}</button>
    </form>
  </section>
</template>

<style scoped>
.catalog-tabs,.catalog-toolbar {display:flex;flex-wrap:wrap;gap:10px;margin:16px 0}
.catalog-tabs .elegido {outline:2px solid #2563eb}
.catalog-toolbar input {flex:1;min-width:190px}
.catalog-form {margin-top:24px;border-top:1px solid #dbe3ed;padding-top:20px;display:grid;gap:14px;max-width:620px}
.catalog-form label {display:grid;gap:6px;font-weight:600}
.catalog-form input,.catalog-form select,.catalog-form textarea,.catalog-toolbar input {padding:10px;border:1px solid #cbd5e1;border-radius:8px;font:inherit;width:100%;box-sizing:border-box}
.catalog-success {color:#166534}
</style>
