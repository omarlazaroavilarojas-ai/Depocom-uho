<script setup>
import { ref, computed, onMounted } from 'vue'
const equipos=ref([]), buscar=ref(''), elegido=ref(null), error=ref(''), cargando=ref(false)
const valor=x=>x==null||x===''?'—':typeof x==='object'?(x.nombre||x.no_inventario||x.codigo||x.id||JSON.stringify(x)):String(x)
const filtrados=computed(()=>equipos.value.filter(x=>JSON.stringify(x).toLowerCase().includes(buscar.value.toLowerCase().trim())))
async function cargar(){cargando.value=true;error.value='';try{const r=await fetch('/api/deposito/equipos/',{credentials:'include'});const d=await r.json().catch(()=>({}));if(!r.ok)throw Error(d.detail||d.error||`HTTP ${r.status}`);equipos.value=Array.isArray(d)?d:Array.isArray(d.results)?d.results:Array.isArray(d.datos)?d.datos:[]}catch(e){error.value=e.message;equipos.value=[]}finally{cargando.value=false}}
onMounted(cargar)
</script>
<template>
<section class="panel data-panel"><div class="panel-title"><h3>Equipos en depósito</h3><span>{{filtrados.length}} RESULTADOS</span></div>
<p>Consulta los equipos recibidos. Las modificaciones y salidas deben registrarse mediante operaciones autorizadas.</p>
<div class="table-toolbar"><div class="search"><input v-model="buscar" placeholder="Buscar equipo, inventario, estado o ubicación…" aria-label="Buscar equipos"/></div><button class="secondary" @click="cargar" :disabled="cargando">Actualizar</button></div>
<p v-if="error" class="form-error">{{error}}</p><p v-if="cargando">Cargando…</p><p v-else-if="!filtrados.length">No se encontraron equipos.</p>
<div v-else class="table-scroll"><table><thead><tr><th>ID</th><th>Equipo</th><th>Estado</th><th>Ubicación</th><th>Acciones</th></tr></thead><tbody><tr v-for="e in filtrados" :key="e.id"><td>{{valor(e.id)}}</td><td>{{valor(e.equipo_nombre||e.equipo)}}</td><td>{{valor(e.estado_nombre||e.estado)}}</td><td>{{valor(e.ubicacion_nombre||e.ubicacion)}}</td><td><button class="secondary" @click="elegido=e">Ver detalles</button></td></tr></tbody></table></div>
<div v-if="elegido" class="panel" style="margin-top:20px"><div class="panel-title"><h3>Detalles #{{elegido.id}}</h3><button class="secondary" @click="elegido=null">Cerrar</button></div><dl class="detalles"><template v-for="(v,k) in elegido" :key="k"><dt>{{k.replaceAll('_',' ')}}</dt><dd>{{valor(v)}}</dd></template></dl></div>
</section>
</template>
<style scoped>.detalles{display:grid;grid-template-columns:minmax(130px,1fr) 2fr;gap:10px 16px;overflow-wrap:anywhere}.detalles dt{font-weight:600;text-transform:capitalize}.detalles dd{margin:0}.table-toolbar{display:flex;gap:12px;flex-wrap:wrap;align-items:center;margin:16px 0}.search{flex:1;min-width:210px}.search input{width:100%;box-sizing:border-box}</style>
