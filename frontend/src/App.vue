<script setup>
import {ref, computed, onMounted, watch} from 'vue'
import SolicitudesBaja from './components/SolicitudesBaja.vue'
import PanelAprobaciones from './components/PanelAprobaciones.vue'
import PanelEconomia from './components/PanelEconomia.vue'
import PanelRecepcion from './components/PanelRecepcion.vue'
import InventarioDeposito from './components/InventarioDeposito.vue'
import GestionInventario from './components/GestionInventario.vue'
import AdministracionCatalogos from './components/AdministracionCatalogos.vue'
import GestionDespiece from './components/GestionDespiece.vue'
import { LayoutDashboard, ClipboardList, CheckCircle2, Wrench, Landmark, Monitor, Cpu, Package, ArrowLeftRight, Route, Settings, Search, Bell, RefreshCw, LogOut, Menu, X, ChevronRight, ShieldCheck, AlertCircle, FileText, Download, Database, UserRound, LockKeyhole, ArrowUpRight } from 'lucide-vue-next'
const menu=[
 {id:'dashboard',name:'Panel general',icon:LayoutDashboard,group:'GENERAL'},
 {id:'solicitudes',name:'Solicitudes de baja',icon:ClipboardList,group:'GESTIÓN'},
 {id:'area',name:'Aprobación de área',icon:CheckCircle2,group:'GESTIÓN'},
 {id:'revision',name:'Revisión técnica',icon:Wrench,group:'GESTIÓN'},
 {id:'economia',name:'Control de economía',icon:Landmark,group:'GESTIÓN'},
 {id:'recepcion',name:'Recepción en depósito',icon:Package,group:'DEPÓSITO'},
 {id:'deposito',name:'Inventario del depósito',icon:Monitor,group:'DEPÓSITO'},
 {id:'despiece',name:'Despiece de equipos',icon:Cpu,group:'DEPÓSITO'},
 {id:'piezas',name:'Almacén de piezas',icon:Package,group:'DEPÓSITO'},
 {id:'extracciones',name:'Extracción e instalación',icon:ArrowLeftRight,group:'DEPÓSITO'},
 {id:'trazabilidad',name:'Trazabilidad y reportes',icon:Route,group:'CONSULTA'},
 {id:'admin',name:'Administración',icon:Settings,group:'SISTEMA'}]
const theme=ref('light')
const dashboardSeries=ref([])
const dashboardLabels=ref([])
const page=ref('dashboard'), sidebar=ref(false), session=ref(null), loading=ref(false), error=ref(''), data=ref([]), search=ref(''), loginUser=ref(''), loginPass=ref(''), loginError=ref(''), logging=ref(false), notices=ref([])
const selected=computed(()=>menu.find(m=>m.id===page.value)||menu[0]); const isLogged=computed(()=>!!session.value?.autenticado)
const menuVisible=computed(()=>{
 const p=session.value?.permisos||{}
 const roles=session.value?.roles||[]
 const admin=!!p.administrar
 const soporte=roles.includes('Jefe de Soporte Técnico')
 const tecnico=roles.includes('Técnico de Soporte')
 const acceso={dashboard:true,solicitudes:!!p.crear_solicitudes,area:!!p.aprobar_area,
 revision:!!p.revision_tecnica,economia:!!p.aprobar_economia,recepcion:admin||soporte,
 deposito:!!p.consultar,despiece:!!p.registrar_piezas||!!p.aprobar_despiece,
 piezas:!!p.consultar,extracciones:!!p.aprobar_extraccion||tecnico,
 trazabilidad:!!p.consultar,admin:admin}
 return menu.filter(m=>!!acceso[m.id])
})
const groups=[...new Set(menu.map(m=>m.group))]
watch(menuVisible, items=>{if(isLogged.value && !items.some(m=>m.id===page.value))page.value='dashboard'})
const endpoints={solicitudes:'/api/solicitudes/',area:'/api/solicitudes/',revision:'/api/solicitudes/',economia:'/api/solicitudes/',deposito:'/api/deposito/equipos/',despiece:'/api/despieces/',piezas:'/api/inventario/',extracciones:'/api/extracciones/',admin:'/api/equipos/'}
const columns={solicitudes:['id','estado','departamento','fecha_creacion'],area:['id','estado','departamento'],revision:['id','estado','departamento'],economia:['id','estado','departamento'],deposito:['id','equipo','estado','ubicacion'],despiece:['id','equipo','estado','fecha_propuesta'],piezas:['id','codigo','nombre','cantidad','estado'],extracciones:['id','estado','pieza','equipo_destino'],admin:['id','no_inventario','marca','modelo','departamento']}
const toRows=v=>Array.isArray(v)?v:Array.isArray(v?.results)?v.results:Array.isArray(v?.datos)?v.datos:[]
async function request(path,options={}){const r=await fetch(path,{credentials:'include',...options});if(!r.ok){let body;try{body=await r.json()}catch{};throw new Error(body?.detail||body?.error||`La API respondió ${r.status}`)}return r.status===204?null:r.json()}
async function refreshSession(){try{session.value=await request('/api/sesion/')}catch(e){session.value={autenticado:false};error.value=e.message}}
async function load(){error.value='';data.value=[];search.value='';if(!isLogged.value)return;if(page.value==='dashboard'){loading.value=true;try{const [sol,equip,piez]=await Promise.allSettled([request('/api/solicitudes/'),request('/api/deposito/equipos/'),request('/api/inventario/')]);const solicitudes=sol.status==='fulfilled'?toRows(sol.value):[];dashboardLabels.value=['Pendientes','Aprobadas','Realizadas'];dashboardSeries.value=[solicitudes.filter(x=>String(x.estado||'').toLowerCase().includes('pendiente')).length,solicitudes.filter(x=>String(x.estado||'').toLowerCase().includes('aprob')).length,solicitudes.filter(x=>['realizada','realizado','completada','completado'].includes(String(x.estado||'').toLowerCase())).length];notices.value=[{name:'Solicitudes',value:sol.status==='fulfilled'?toRows(sol.value).length:'—',icon:ClipboardList},{name:'Equipos en depósito',value:equip.status==='fulfilled'?toRows(equip.value).length:'—',icon:Monitor},{name:'Referencias de piezas',value:piez.status==='fulfilled'?toRows(piez.value).length:'—',icon:Package}];if([sol,equip,piez].every(x=>x.status==='rejected'))error.value='No se pudieron consultar los módulos. Comprueba que Django esté ejecutándose.'}finally{loading.value=false}return}
 if(!endpoints[page.value])return;loading.value=true;try{data.value=toRows(await request(endpoints[page.value]))}catch(e){error.value=e.message}finally{loading.value=false}}
watch(page,load);onMounted(async()=>{await refreshSession();await load()})
function toggleTheme(){theme.value=theme.value==='light'?'dark':'light'}
function navigate(id){if(!menuVisible.value.some(m=>m.id===id))return;page.value=id;sidebar.value=false}
function label(k){return ({no_inventario:'Inventario',fecha_creacion:'Fecha',fecha_propuesta:'Fecha propuesta',equipo_destino:'Equipo destino'})[k]||k.replaceAll('_',' ')}
function value(v){if(v===null||v===undefined||v==='')return '—';if(typeof v==='object')return v.nombre||v.no_inventario||v.codigo||v.id||'—';if(typeof v==='boolean')return v?'Sí':'No';return String(v)}
const filtered=computed(()=>data.value.filter(item=>JSON.stringify(item).toLowerCase().includes(search.value.toLowerCase())))
async function login(){loginError.value='';logging.value=true;try{await request('/api/csrf/');const token=document.cookie.split('; ').find(x=>x.startsWith('csrftoken='))?.split('=')[1]||'';await request('/api/login/',{method:'POST',headers:{'Content-Type':'application/json','X-CSRFToken':decodeURIComponent(token)},body:JSON.stringify({usuario:loginUser.value,contrasena:loginPass.value})});loginPass.value='';await refreshSession();await load()}catch(e){loginError.value=e.message}finally{logging.value=false}}
async function logout(){try{const token=document.cookie.split('; ').find(x=>x.startsWith('csrftoken='))?.split('=')[1]||'';await request('/api/logout/',{method:'POST',headers:{'X-CSRFToken':decodeURIComponent(token)}})}catch(e){error.value=e.message}await refreshSession();data.value=[]}
function openReport(type,format){window.open(`/api/reportes/${type}.${format}`,'_blank','noopener,noreferrer')}
</script>
<template>
<div class="app-shell" :class="{'theme-dark':theme==='dark'}">
 <div v-if="sidebar" class="scrim" @click="sidebar=false"></div>
 <aside class="sidebar" :class="{open:sidebar}">
  <div class="brand"><div class="brand-mark"><img src="/logo-uho.png" alt="Logotipo de la Universidad de Holguín" class="uho-brand-logo" /></div><div><strong>DepoCom <span>UHO</span></strong><small>Gestión institucional</small></div><button class="mobile-close" aria-label="Cerrar menú" @click="sidebar=false"><X :size="20"/></button></div>
  <div class="sidebar-inner"><template v-for="group in groups" :key="group"><div v-if="menuVisible.some(x=>x.group===group)" class="nav-heading">{{group}}</div><button v-for="m in menuVisible.filter(x=>x.group===group)" :key="m.id" class="nav-item" :class="{active:page===m.id}" @click="navigate(m.id)"><component :is="m.icon" :size="18"/><span>{{m.name}}</span><ChevronRight v-if="page===m.id" :size="15" class="nav-arrow"/></button></template></div>
  <div class="sidebar-foot"><ShieldCheck :size="17"/><span>Universidad de Holguín<br><small>Sistema de gestión · UHO</small></span></div>
 </aside>
 <div class="workspace">
  <header class="topbar"><div class="top-left"><button class="menu-button" aria-label="Abrir menú" @click="sidebar=true"><Menu :size="22"/></button><span class="breadcrumb">DepoCom UHO</span><ChevronRight :size="15" class="chev"/><strong>{{selected.name}}</strong></div><div class="top-actions"><span class="system-pill"><span class="online-dot"></span> Entorno local</span><button class="icon-button theme-toggle" :title="theme==='dark'?'Cambiar a tema claro':'Cambiar a tema oscuro'" @click="toggleTheme">{{theme==='dark'?'☀':'☾'}}</button><button class="icon-button" title="Actualizar" @click="load"><RefreshCw :size="18"/></button><div class="avatar"><UserRound :size="18"/></div></div></header>
  <main class="content">
   <div class="page-intro"><div><div class="eyebrow">UNIVERSIDAD DE HOLGUÍN / DEPOCOM</div><h1>{{selected.name}}</h1><p>{{page==='dashboard'?'Visión general de la gestión de equipos y piezas de cómputo.':page==='trazabilidad'?'Consulta de informes y seguimiento de movimientos.':page==='admin'?'Gestión de sedes, áreas, departamentos y tipos de recursos.':'Consulta de registros y operaciones del módulo.'}}</p></div><button v-if="isLogged" class="secondary refresh" @click="load"><RefreshCw :size="16"/> Actualizar</button></div>
   <div v-if="!isLogged" class="login-wrap"><div class="login-art"><div class="login-icon"><LockKeyhole :size="27"/></div><h2>Bienvenido a DepoCom</h2><p>Accede con tu cuenta habilitada en el sistema para consultar la información del depósito.</p><div class="login-note"><ShieldCheck :size="18"/> Acceso protegido por sesión de Django</div></div><form class="login-card" @submit.prevent="login"><h2>Iniciar sesión</h2><p>Introduce tus credenciales para continuar.</p><label>Usuario<input v-model="loginUser" autocomplete="username" required placeholder="Nombre de usuario"/></label><label>Contraseña<input v-model="loginPass" type="password" autocomplete="current-password" required placeholder="••••••••"/></label><p v-if="loginError" class="form-error">{{loginError}}</p><button class="primary full" :disabled="logging">{{logging?'Accediendo…':'Entrar al sistema'}} <ArrowUpRight :size="17"/></button></form></div>
   <template v-else>
    <div class="welcome"><div><span class="welcome-label">SESIÓN ACTIVA</span><h2>Bienvenido{{session?.usuario?' de nuevo, '+session.usuario:''}}</h2><p>Rol: {{session?.roles?.join(', ') || 'Sin rol asignado'}} · Información obtenida del backend.</p></div><button class="logout" @click="logout"><LogOut :size="16"/> Cerrar sesión</button></div>
    <div v-if="error" class="error-banner"><AlertCircle :size="18"/><span>{{error}}</span><button @click="load">Reintentar</button></div>
    <template v-if="page==='dashboard'"><div class="stats"><div v-for="n in notices" :key="n.name" class="stat-card"><div class="stat-head"><span>{{n.name}}</span><div class="stat-icon"><component :is="n.icon" :size="20"/></div></div><strong>{{n.value}}</strong><small>Registros consultados</small></div></div><div class="analytics-panel panel" v-if="dashboardSeries.length"><div class="panel-title"><h3>Estado de solicitudes</h3><span>DATOS REALES</span></div><div class="analytics-body"><div class="chart-bars"><div v-for="(count,i) in dashboardSeries" :key="dashboardLabels[i]" class="chart-col"><strong>{{count}}</strong><div class="chart-track"><div class="chart-fill" :style="{height: (dashboardSeries.some(n=>n>0)?Math.max(5,count/Math.max(...dashboardSeries)*100):0)+'%'}"></div></div><span>{{dashboardLabels[i]}}</span></div></div><p>Distribución de solicitudes consultadas. Si una categoría no aparece en los datos, se muestra con valor cero.</p></div></div><div class="two-col"><div class="panel"><div class="panel-title"><h3>Accesos rápidos</h3><span>OPERACIONES</span></div><div class="quick-grid"><button v-for="m in menuVisible.filter(m=>['solicitudes','deposito','piezas','trazabilidad'].includes(m.id))" :key="m.id" @click="navigate(m.id)"><span class="quick-icon"><component :is="m.icon" :size="21"/></span><span>{{m.name}}</span><ChevronRight :size="17"/></button></div></div><div class="panel"><div class="panel-title"><h3>Estado del sistema</h3><span>INTEGRACIÓN</span></div><div class="status-list"><div><CheckCircle2 :size="19"/><span>Conexión con Django</span><strong>Activa</strong></div><div><CheckCircle2 :size="19"/><span>Sesión de usuario</span><strong>Autenticada</strong></div><div><FileText :size="19"/><span>Documentación de API</span><a href="/api/docs/" target="_blank" rel="noopener">Abrir <ArrowUpRight :size="14"/></a></div></div></div></div></template>
    <SolicitudesBaja v-else-if="page==='solicitudes'" :request="request" @changed="load"/>
    <PanelAprobaciones v-else-if="page==='area'" :sesion="session" modo="area"/>
    <PanelAprobaciones v-else-if="page==='revision'" :sesion="session" modo="revision"/>
    <PanelEconomia v-else-if="page==='economia'" :sesion="session"/>
    <PanelRecepcion v-else-if="page==='recepcion'" :sesion="session"/>
    <InventarioDeposito v-else-if="page==='deposito'"/>
    <GestionDespiece v-else-if="page==='despiece'" :sesion="session"/>
    <GestionInventario v-else-if="page==='piezas'" :sesion="session"/>
    <AdministracionCatalogos v-else-if="page==='admin'" :sesion="session"/>
    <div v-else-if="page==='trazabilidad'" class="panel reports"><div class="panel-title"><h3>Centro de reportes</h3><span>EXPORTACIONES</span></div><p>Descarga informes de los módulos habilitados. El backend comprobará tus permisos antes de permitir cada exportación.</p><div class="report-grid"><div v-for="r in [{id:'equipos-deposito',name:'Equipos en depósito'},{id:'movimientos-piezas',name:'Movimientos de piezas'},{id:'solicitudes',name:'Solicitudes de baja'},{id:'historial-solicitudes',name:'Historial de solicitudes'},{id:'trazabilidad-piezas',name:'Trazabilidad de piezas'}]" :key="r.id" class="report-item"><div><FileText :size="20"/><strong>{{r.name}}</strong></div><div class="report-buttons"><button @click="openReport(r.id,'pdf')"><Download :size="14"/> PDF</button><button @click="openReport(r.id,'xlsx')"><Download :size="14"/> Excel</button></div></div></div><small class="report-help">Las rutas de descarga pueden variar según la versión del backend; compruébalas en Swagger.</small></div>
    <div v-else class="panel data-panel"><div class="panel-title"><h3>Registros del módulo</h3><span>{{filtered.length}} RESULTADOS</span></div><div class="table-toolbar"><div class="search"><Search :size="17"/><input v-model="search" placeholder="Buscar en los registros…" aria-label="Buscar registros"/></div><span class="read-only">Vista de consulta</span></div><div v-if="loading" class="empty">Cargando registros…</div><div v-else-if="!filtered.length" class="empty"><Database :size="30"/><strong>Sin registros para mostrar</strong><p>{{search?'Prueba otra búsqueda.':'No se encontraron registros o no hay datos disponibles.'}}</p></div><div v-else class="table-scroll"><table><thead><tr><th v-for="col in columns[page]" :key="col">{{label(col)}}</th></tr></thead><tbody><tr v-for="(row,i) in filtered" :key="row.id??i"><td v-for="col in columns[page]" :key="col"><span v-if="col==='estado'" class="state-pill">{{value(row[col])}}</span><template v-else>{{value(row[col])}}</template></td></tr></tbody></table></div><div class="table-footer">Mostrando {{filtered.length}} registros · Datos reales de la API</div></div>
   </template>
  </main><footer class="footer">DepoCom UHO · Universidad de Holguín <span>Interfaz Vue 3 · Primera etapa</span></footer>
 </div>
</div>
</template>
