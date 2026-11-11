
<script setup>
import { computed, ref, watch } from 'vue'

import {
  obtenerInventario,
  crearPieza,
  actualizarPieza,
} from '../api/inventario'

const props = defineProps({
  sesion: {
    type: Object,
    required: true,
  },
})

const piezas = ref([])
const busqueda = ref('')
const piezaEditar = ref(null)

const codigo = ref('')
const nombre = ref('')
const descripcion = ref('')
const cantidad = ref(0)
const estado = ref('disponible')
const ubicacion = ref('')

const cargando = ref(false)
const guardando = ref(false)
const error = ref('')
const mensaje = ref('')

const puedeGestionar = computed(() => Boolean(
  props.sesion.autenticado &&
  props.sesion.puede_crear_equipos
))

const modoEdicion = computed(() =>
  piezaEditar.value !== null
)

const piezasFiltradas = computed(() => {
  const texto = busqueda.value.trim().toLowerCase()

  if (!texto) return piezas.value

  return piezas.value.filter((pieza) =>
    [
      pieza.codigo,
      pieza.nombre,
      pieza.descripcion,
      pieza.ubicacion,
      pieza.estado_nombre,
    ].some((valor) =>
      String(valor || '').toLowerCase().includes(texto)
    )
  )
})

const totalUnidades = computed(() =>
  piezas.value.reduce(
    (total, pieza) => total + Number(pieza.cantidad),
    0
  )
)

async function cargarInventario() {
  if (!props.sesion.autenticado) {
    piezas.value = []
    return
  }

  cargando.value = true
  error.value = ''

  try {
    const datos = await obtenerInventario()
    piezas.value = Array.isArray(datos) ? datos : datos.results || []
  } catch (err) {
    error.value =
      err.message || 'No se pudo cargar el inventario.'
  } finally {
    cargando.value = false
  }
}

function limpiarFormulario() {
  piezaEditar.value = null
  codigo.value = ''
  nombre.value = ''
  descripcion.value = ''
  cantidad.value = 0
  estado.value = 'disponible'
  ubicacion.value = ''
}

function editarPieza(pieza) {
  if (!puedeGestionar.value) return

  piezaEditar.value = pieza.id
  codigo.value = pieza.codigo
  nombre.value = pieza.nombre
  descripcion.value = pieza.descripcion || ''
  cantidad.value = pieza.cantidad
  estado.value = pieza.estado
  ubicacion.value = pieza.ubicacion || ''

  error.value = ''
  mensaje.value = ''

  document.getElementById('formulario-inventario')
    ?.scrollIntoView({
      behavior: 'smooth',
      block: 'start',
    })
}

async function guardarPieza() {
  error.value = ''
  mensaje.value = ''

  if (!puedeGestionar.value) {
    error.value = 'No tienes permisos para gestionar el inventario.'
    return
  }

  if (!codigo.value.trim() || !nombre.value.trim()) {
    error.value = 'El código y el nombre son obligatorios.'
    return
  }

  if (
    !modoEdicion.value &&
    (!Number.isInteger(Number(cantidad.value)) ||
      Number(cantidad.value) < 0)
  ) {
    error.value = 'La existencia inicial debe ser un entero no negativo.'
    return
  }

  const datos = {
    codigo: codigo.value.trim(),
    nombre: nombre.value.trim(),
    descripcion: descripcion.value.trim(),
    estado: estado.value,
    ubicacion: ubicacion.value.trim(),
  }

  // La cantidad solamente se envía al crear una pieza.
  // Las modificaciones posteriores se hacen mediante movimientos.
  if (!modoEdicion.value) {
    datos.cantidad = Number(cantidad.value)
  }

  guardando.value = true

  try {
    if (modoEdicion.value) {
      await actualizarPieza(piezaEditar.value, datos)
      mensaje.value = 'Pieza actualizada correctamente.'
    } else {
      await crearPieza(datos)
      mensaje.value = 'Pieza registrada correctamente.'
    }

    limpiarFormulario()
    await cargarInventario()
  } catch (err) {
    error.value = err.message || 'No se pudo guardar la pieza.'
  } finally {
    guardando.value = false
  }
}

function actualizarInventarioDesdeMovimiento() {
  if (props.sesion.autenticado) {
    return cargarInventario()
  }
}

defineExpose({
  actualizarInventarioDesdeMovimiento,
})

watch(
  () => props.sesion.autenticado,
  (autenticado) => {
    if (autenticado) {
      cargarInventario()
    } else {
      piezas.value = []
      limpiarFormulario()
      busqueda.value = ''
      error.value = ''
      mensaje.value = ''
    }
  },
  { immediate: true }
)

watch(
  () => props.sesion.puede_crear_equipos,
  (permitido) => {
    if (!permitido) limpiarFormulario()
  }
)
</script>

<template>
  <section class="inventario">
    <div class="cabecera">
      <div>
        <h2>Inventario del depósito</h2>
        <p>
          Registro y control de piezas y componentes
          informáticos almacenados.
        </p>
      </div>

      <button
        v-if="sesion.autenticado"
        type="button"
        class="secundario"
        :disabled="cargando"
        @click="cargarInventario"
      >
        Actualizar inventario
      </button>
    </div>

    <p v-if="!sesion.autenticado" class="aviso">
      Inicia sesión para consultar el inventario.
    </p>

    <template v-else>
      <div class="resumen">
        <div class="indicador">
          <span>Referencias registradas</span>
          <strong>{{ piezas.length }}</strong>
        </div>

        <div class="indicador">
          <span>Unidades registradas</span>
          <strong>{{ totalUnidades }}</strong>
        </div>
      </div>

      <div
        v-if="puedeGestionar"
        id="formulario-inventario"
        class="formulario"
      >
        <h3>
          {{
            modoEdicion
              ? 'Editar pieza del depósito'
              : 'Registrar nueva pieza'
          }}
        </h3>

        <form @submit.prevent="guardarPieza">
          <fieldset :disabled="guardando">
            <div class="campos-grid">
              <div class="campo">
                <label for="pieza-codigo">Código *</label>
                <input
                  id="pieza-codigo"
                  v-model="codigo"
                  maxlength="50"
                  placeholder="Ejemplo: RAM-001"
                  required
                />
              </div>

              <div class="campo">
                <label for="pieza-nombre">Nombre *</label>
                <input
                  id="pieza-nombre"
                  v-model="nombre"
                  maxlength="150"
                  placeholder="Ejemplo: Memoria RAM"
                  required
                />
              </div>

              <div v-if="!modoEdicion" class="campo">
                <label for="pieza-cantidad">
                  Existencia inicial *
                </label>
                <input
                  id="pieza-cantidad"
                  v-model.number="cantidad"
                  type="number"
                  min="0"
                  step="1"
                  required
                />
              </div>

              <div v-else class="campo">
                <label>Existencias actuales</label>
                <div class="existencias-actuales">
                  <strong>{{ cantidad }} unidades</strong>
                  <small>
                    Las existencias se modifican desde
                    el módulo de movimientos.
                  </small>
                </div>
              </div>

              <div class="campo">
                <label for="pieza-estado">Estado</label>
                <select id="pieza-estado" v-model="estado">
                  <option value="disponible">Disponible</option>
                  <option value="revision">En revisión</option>
                  <option value="no_utilizable">No utilizable</option>
                </select>
              </div>

              <div class="campo">
                <label for="pieza-ubicacion">Ubicación</label>
                <input
                  id="pieza-ubicacion"
                  v-model="ubicacion"
                  maxlength="150"
                  placeholder="Ejemplo: Estante A"
                />
              </div>
            </div>

            <div class="campo">
              <label for="pieza-descripcion">Descripción</label>
              <textarea
                id="pieza-descripcion"
                v-model="descripcion"
                rows="3"
                placeholder="Características de la pieza..."
              />
            </div>

            <div class="acciones">
              <button type="submit">
                {{
                  guardando
                    ? 'Guardando...'
                    : modoEdicion
                      ? 'Guardar cambios'
                      : 'Registrar pieza'
                }}
              </button>

              <button
                v-if="modoEdicion"
                type="button"
                class="secundario"
                @click="limpiarFormulario"
              >
                Cancelar edición
              </button>
            </div>
          </fieldset>
        </form>
      </div>

      <div class="listado">
        <h3>Piezas registradas</h3>

        <div class="campo">
          <label for="buscar-pieza">
            Buscar en el inventario
          </label>
          <input
            id="buscar-pieza"
            v-model="busqueda"
            placeholder="Código, nombre, estado o ubicación..."
          />
        </div>

        <p v-if="cargando">Cargando inventario...</p>

        <p v-else-if="piezasFiltradas.length === 0">
          No se encontraron piezas.
        </p>

        <div v-else class="tabla-contenedor">
          <table>
            <thead>
              <tr>
                <th>Código</th>
                <th>Nombre</th>
                <th>Cantidad</th>
                <th>Estado</th>
                <th>Ubicación</th>
                <th v-if="puedeGestionar">Acciones</th>
              </tr>
            </thead>

            <tbody>
              <tr
                v-for="pieza in piezasFiltradas"
                :key="pieza.id"
              >
                <td>{{ pieza.codigo }}</td>
                <td>{{ pieza.nombre }}</td>
                <td>{{ pieza.cantidad }}</td>
                <td>{{ pieza.estado_nombre }}</td>
                <td>{{ pieza.ubicacion || '—' }}</td>
                <td v-if="puedeGestionar">
                  <button
                    type="button"
                    class="secundario"
                    @click="editarPieza(pieza)"
                  >
                    Editar
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>

    <p v-if="mensaje" class="mensaje" role="status">
      {{ mensaje }}
    </p>

    <p v-if="error" class="error" role="alert">
      {{ error }}
    </p>
  </section>
</template>

<style scoped>
.inventario {
  margin-top: 36px;
  padding: 24px;
  background: white;
  border: 1px solid #d7e0e8;
  border-radius: 12px;
}

h2, h3 { color: #123b5d; }

.cabecera {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.resumen {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin: 24px 0;
}

.indicador {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 20px;
  background: #eaf1f7;
  border-radius: 10px;
}

.indicador strong {
  font-size: 28px;
  color: #123b5d;
}

.formulario {
  margin-top: 24px;
  padding: 20px;
  border: 1px solid #d7e0e8;
  border-radius: 10px;
  background: #f7f9fc;
  scroll-margin-top: 20px;
}

fieldset {
  border: 0;
  padding: 0;
  margin: 0;
  min-width: 0;
}

.campos-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0 16px;
}

.campo {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin: 14px 0;
}

.campo input,
.campo select,
.campo textarea {
  padding: 12px;
  border: 1px solid #ccd8e2;
  border-radius: 8px;
  font: inherit;
  background: white;
}

.existencias-actuales {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 12px;
  background: #eaf1f7;
  border-radius: 8px;
}

.existencias-actuales small {
  color: #526779;
}

.acciones {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-top: 16px;
}

button {
  padding: 10px 16px;
  border: none;
  border-radius: 8px;
  background: #123b5d;
  color: white;
  cursor: pointer;
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.secundario {
  background: white;
  color: #123b5d;
  border: 1px solid #123b5d;
}

.listado { margin-top: 32px; }

.tabla-contenedor { overflow-x: auto; }

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 12px;
  border-bottom: 1px solid #d7e0e8;
  text-align: left;
}

th {
  background: #f2f6fa;
  color: #123b5d;
}

.aviso { color: #755014; }

.mensaje {
  margin-top: 20px;
  padding: 12px;
  background: #eaf7ee;
  color: #175c37;
  border-radius: 8px;
}

.error {
  margin-top: 20px;
  padding: 12px;
  background: #fff0ef;
  color: #b42318;
  border-radius: 8px;
}

@media (max-width: 700px) {
  .inventario { padding: 14px; }
  .campos-grid, .resumen { grid-template-columns: 1fr; }
  .cabecera {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
