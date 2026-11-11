
<script setup>
import { computed, ref, watch } from 'vue'

import { obtenerInventario } from '../api/inventario'

import {
  obtenerMovimientos,
  registrarMovimiento,
} from '../api/movimientos'

const props = defineProps({
  sesion: {
    type: Object,
    required: true,
  },
})

const emit = defineEmits([
  'movimiento-registrado',
])

const piezas = ref([])
const movimientos = ref([])

const piezaId = ref('')
const tipo = ref('entrada')
const cantidad = ref(1)
const motivo = ref('')

const cargando = ref(false)
const guardando = ref(false)
const error = ref('')
const mensaje = ref('')

const puedeGestionar = computed(() => Boolean(
  props.sesion.autenticado &&
  props.sesion.puede_crear_equipos
))

const piezaSeleccionada = computed(() =>
  piezas.value.find(
    (pieza) => pieza.id === Number(piezaId.value)
  )
)

async function cargarDatos() {
  if (!props.sesion.autenticado) {
    piezas.value = []
    movimientos.value = []
    return
  }

  cargando.value = true
  error.value = ''

  try {
    const [datosPiezas, datosMovimientos] =
      await Promise.all([
        obtenerInventario(),
        obtenerMovimientos(),
      ])

    piezas.value = Array.isArray(datosPiezas)
      ? datosPiezas
      : datosPiezas.results || []

    movimientos.value = Array.isArray(datosMovimientos)
      ? datosMovimientos
      : datosMovimientos.results || []
  } catch (err) {
    error.value =
      err.message || 'No se pudieron cargar los movimientos.'
  } finally {
    cargando.value = false
  }
}

function limpiarFormulario() {
  piezaId.value = ''
  tipo.value = 'entrada'
  cantidad.value = 1
  motivo.value = ''
}

async function guardarMovimiento() {
  error.value = ''
  mensaje.value = ''

  if (!puedeGestionar.value) {
    error.value = 'No tienes permisos para registrar movimientos.'
    return
  }

  if (!piezaId.value) {
    error.value = 'Selecciona una pieza.'
    return
  }

  if (
    !Number.isInteger(Number(cantidad.value)) ||
    Number(cantidad.value) <= 0
  ) {
    error.value = 'La cantidad debe ser un entero positivo.'
    return
  }

  if (
    tipo.value === 'salida' &&
    piezaSeleccionada.value &&
    Number(cantidad.value) > piezaSeleccionada.value.cantidad
  ) {
    error.value =
      'No hay suficientes existencias para esta salida.'
    return
  }

  if (!motivo.value.trim()) {
    error.value = 'Debes indicar el motivo del movimiento.'
    return
  }

  guardando.value = true

  try {
    await registrarMovimiento({
      pieza: Number(piezaId.value),
      tipo: tipo.value,
      cantidad: Number(cantidad.value),
      motivo: motivo.value.trim(),
    })

    emit('movimiento-registrado')

    limpiarFormulario()
    mensaje.value = 'Movimiento registrado correctamente.'

    await cargarDatos()
  } catch (err) {
    error.value =
      err.message || 'No se pudo registrar el movimiento.'
  } finally {
    guardando.value = false
  }
}

watch(
  () => props.sesion.autenticado,
  (autenticado) => {
    if (autenticado) {
      cargarDatos()
    } else {
      piezas.value = []
      movimientos.value = []
      limpiarFormulario()
      error.value = ''
      mensaje.value = ''
    }
  },
  { immediate: true }
)
</script>

<template>
  <section class="movimientos">
    <h2>Movimientos del depósito</h2>

    <p>
      Registro de entradas y salidas de piezas
      con control de existencias e historial.
    </p>

    <p v-if="!sesion.autenticado" class="aviso">
      Inicia sesión para consultar los movimientos.
    </p>

    <template v-else>
      <div v-if="puedeGestionar" class="formulario">
        <h3>Registrar movimiento</h3>

        <form @submit.prevent="guardarMovimiento">
          <fieldset :disabled="guardando">
            <div class="campo">
              <label for="movimiento-pieza">Pieza *</label>
              <select
                id="movimiento-pieza"
                v-model="piezaId"
                required
              >
                <option value="">Selecciona una pieza</option>
                <option
                  v-for="pieza in piezas"
                  :key="pieza.id"
                  :value="String(pieza.id)"
                >
                  {{ pieza.codigo }} —
                  {{ pieza.nombre }}
                  ({{ pieza.cantidad }} disponibles)
                </option>
              </select>
            </div>

            <p
              v-if="piezaSeleccionada"
              class="existencias"
            >
              Existencias actuales:
              <strong>{{ piezaSeleccionada.cantidad }}</strong>
            </p>

            <div class="campo">
              <label for="movimiento-tipo">
                Tipo de movimiento *
              </label>
              <select id="movimiento-tipo" v-model="tipo">
                <option value="entrada">Entrada</option>
                <option value="salida">Salida</option>
              </select>
            </div>

            <div class="campo">
              <label for="movimiento-cantidad">
                Cantidad *
              </label>
              <input
                id="movimiento-cantidad"
                v-model.number="cantidad"
                type="number"
                min="1"
                step="1"
                required
              />
            </div>

            <div class="campo">
              <label for="movimiento-motivo">
                Motivo *
              </label>
              <textarea
                id="movimiento-motivo"
                v-model="motivo"
                rows="3"
                maxlength="2000"
                placeholder="Describe el motivo del movimiento..."
                required
              />
            </div>

            <button type="submit">
              {{
                guardando
                  ? 'Registrando...'
                  : 'Registrar movimiento'
              }}
            </button>
          </fieldset>
        </form>
      </div>

      <div class="listado">
        <div class="cabecera">
          <h3>Historial de movimientos</h3>

          <button
            type="button"
            class="secundario"
            :disabled="cargando"
            @click="cargarDatos"
          >
            Actualizar
          </button>
        </div>

        <p v-if="cargando">Cargando movimientos...</p>

        <p v-else-if="movimientos.length === 0">
          No hay movimientos registrados.
        </p>

        <div v-else class="tabla-contenedor">
          <table>
            <thead>
              <tr>
                <th>Fecha</th>
                <th>Pieza</th>
                <th>Tipo</th>
                <th>Cantidad</th>
                <th>Anterior</th>
                <th>Posterior</th>
                <th>Usuario</th>
                <th>Motivo</th>
              </tr>
            </thead>

            <tbody>
              <tr
                v-for="movimiento in movimientos"
                :key="movimiento.id"
              >
                <td>
                  {{
                    new Date(
                      movimiento.fecha
                    ).toLocaleString()
                  }}
                </td>
                <td>{{ movimiento.pieza_codigo }}</td>
                <td>
                  <span
                    class="tipo"
                    :class="movimiento.tipo"
                  >
                    {{ movimiento.tipo_nombre }}
                  </span>
                </td>
                <td>{{ movimiento.cantidad }}</td>
                <td>{{ movimiento.existencia_anterior }}</td>
                <td>{{ movimiento.existencia_posterior }}</td>
                <td>{{ movimiento.usuario_nombre }}</td>
                <td>{{ movimiento.motivo }}</td>
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
.movimientos {
  margin-top: 36px;
  padding: 24px;
  background: white;
  border: 1px solid #d7e0e8;
  border-radius: 12px;
}

h2, h3 { color: #123b5d; }

.formulario {
  margin-top: 24px;
  padding: 20px;
  border: 1px solid #d7e0e8;
  border-radius: 10px;
  background: #f7f9fc;
}

fieldset {
  border: 0;
  padding: 0;
  margin: 0;
}

.campo {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin: 16px 0;
}

.campo input,
.campo select,
.campo textarea {
  padding: 12px;
  border: 1px solid #ccd8e2;
  border-radius: 8px;
  background: white;
  font: inherit;
}

.existencias {
  padding: 12px;
  background: #eaf1f7;
  border-radius: 8px;
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

.cabecera {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

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

th { background: #f2f6fa; }

.tipo {
  padding: 5px 10px;
  border-radius: 20px;
  font-size: 12px;
}

.tipo.entrada {
  background: #e8f5e9;
  color: #226c38;
}

.tipo.salida {
  background: #fff3df;
  color: #8a5b16;
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
  .movimientos { padding: 14px; }
  .cabecera {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
