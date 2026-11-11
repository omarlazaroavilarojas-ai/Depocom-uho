
<script setup>
import { reactive, ref, watch } from 'vue'
import {
  registrarEquipo,
  actualizarEquipo,
} from '../api/sesion'

const props = defineProps({
  tiposRecursos: {
    type: Array,
    required: true,
  },
  departamentos: {
    type: Array,
    required: true,
  },
  puedeCrear: {
    type: Boolean,
    default: false,
  },
  equipoEditar: {
    type: Object,
    default: null,
  },
})

const emit = defineEmits([
  'equipo-guardado',
  'cancelar-edicion',
])

const formulario = reactive({
  no_inventario: '',
  tipo_recurso: '',
  marca: '',
  modelo: '',
  no_serie: '',
  departamento: '',
})

const error = ref('')
const mensaje = ref('')
const guardando = ref(false)

watch(
  () => props.equipoEditar,
  (equipo) => {
    error.value = ''
    mensaje.value = ''

    if (!equipo) {
      limpiarFormulario()
      return
    }

    formulario.no_inventario = equipo.no_inventario
    formulario.tipo_recurso = String(equipo.tipo_recurso)
    formulario.marca = equipo.marca || ''
    formulario.modelo = equipo.modelo || ''
    formulario.no_serie = equipo.no_serie || ''
    formulario.departamento = equipo.departamento
      ? String(equipo.departamento)
      : ''
  },
  { immediate: true }
)

function limpiarFormulario() {
  formulario.no_inventario = ''
  formulario.tipo_recurso = ''
  formulario.marca = ''
  formulario.modelo = ''
  formulario.no_serie = ''
  formulario.departamento = ''
}

function cancelarEdicion() {
  limpiarFormulario()
  error.value = ''
  mensaje.value = ''
  emit('cancelar-edicion')
}

async function guardarEquipo() {
  error.value = ''
  mensaje.value = ''

  if (!formulario.no_inventario.trim()) {
    error.value = 'El número de inventario es obligatorio.'
    return
  }

  if (!formulario.tipo_recurso) {
    error.value = 'Selecciona un tipo de recurso.'
    return
  }

  const datos = {
    no_inventario: formulario.no_inventario.trim(),
    tipo_recurso: Number(formulario.tipo_recurso),
    marca: formulario.marca.trim(),
    modelo: formulario.modelo.trim(),
    no_serie: formulario.no_serie.trim(),
    departamento: formulario.departamento
      ? Number(formulario.departamento)
      : null,
  }

  guardando.value = true

  try {
    if (props.equipoEditar) {
      await actualizarEquipo(props.equipoEditar.id, datos)
      mensaje.value = 'Equipo actualizado correctamente.'
    } else {
      await registrarEquipo(datos)
      mensaje.value = 'Equipo registrado correctamente.'
    }

    limpiarFormulario()
    emit('equipo-guardado')
  } catch (err) {
    error.value = err.message
  } finally {
    guardando.value = false
  }
}
</script>

<template>
  <section class="formulario-equipo">
    <h2>
      {{ equipoEditar ? 'Editar equipo' : 'Registrar equipo informático' }}
    </h2>

    <p v-if="!puedeCrear" class="aviso">
      Inicia sesión con una cuenta autorizada
      para registrar o editar equipos.
    </p>

    <form @submit.prevent="guardarEquipo">
      <fieldset :disabled="!puedeCrear || guardando">
        <div class="campos">
          <div class="campo">
            <label for="inventario">Número de inventario *</label>
            <input
              id="inventario"
              v-model="formulario.no_inventario"
              maxlength="100"
              required
            />
          </div>

          <div class="campo">
            <label for="tipo">Tipo de recurso *</label>
            <select
              id="tipo"
              v-model="formulario.tipo_recurso"
              required
            >
              <option value="">Selecciona un tipo</option>
              <option
                v-for="tipo in tiposRecursos"
                :key="tipo.id"
                :value="String(tipo.id)"
              >
                {{ tipo.nombre }}
              </option>
            </select>
          </div>

          <div class="campo">
            <label for="marca">Marca</label>
            <input
              id="marca"
              v-model="formulario.marca"
              maxlength="150"
            />
          </div>

          <div class="campo">
            <label for="modelo">Modelo</label>
            <input
              id="modelo"
              v-model="formulario.modelo"
              maxlength="150"
            />
          </div>

          <div class="campo">
            <label for="serie">Número de serie</label>
            <input
              id="serie"
              v-model="formulario.no_serie"
              maxlength="150"
            />
          </div>

          <div class="campo">
            <label for="departamento">Departamento</label>
            <select
              id="departamento"
              v-model="formulario.departamento"
            >
              <option value="">Sin asignar</option>
              <option
                v-for="dep in departamentos"
                :key="dep.id"
                :value="String(dep.id)"
              >
                {{ dep.nombre }} — {{ dep.area_nombre }}
              </option>
            </select>
          </div>
        </div>

        <div class="acciones">
          <button type="submit" class="principal">
            {{ guardando ? 'Guardando...' : equipoEditar ? 'Actualizar equipo' : 'Guardar equipo' }}
          </button>

          <button
            type="button"
            class="secundario"
            @click="cancelarEdicion"
          >
            {{ equipoEditar ? 'Cancelar edición' : 'Limpiar' }}
          </button>
        </div>
      </fieldset>
    </form>

    <p v-if="mensaje" class="mensaje" role="status">
      {{ mensaje }}
    </p>

    <p v-if="error" class="error" role="alert">
      {{ error }}
    </p>
  </section>
</template>

<style scoped>
.formulario-equipo {
  margin-top: 36px;
  padding: 24px;
  background: white;
  border: 1px solid #d7e0e8;
  border-radius: 12px;
}

h2 {
  color: #123b5d;
}

.aviso {
  padding: 12px;
  background: #fff4dd;
  color: #755014;
  border-radius: 8px;
}

fieldset {
  border: 0;
  padding: 0;
  margin: 0;
  min-width: 0;
}

fieldset:disabled {
  opacity: 0.65;
}

.campos {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 20px;
}

.campo {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.campo label {
  font-weight: 600;
  color: #123b5d;
}

.campo input,
.campo select {
  box-sizing: border-box;
  width: 100%;
  padding: 12px;
  border: 1px solid #ccd8e2;
  border-radius: 8px;
  background: white;
  color: #263746;
  font-size: 14px;
}

.acciones {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 24px;
}

.acciones button {
  padding: 12px 20px;
  border-radius: 8px;
  cursor: pointer;
}

.principal {
  background: #123b5d;
  color: white;
  border: none;
}

.secundario {
  background: white;
  color: #123b5d;
  border: 1px solid #123b5d;
}

.mensaje,
.error {
  margin-top: 20px;
  padding: 12px;
  border-radius: 8px;
}

.mensaje {
  background: #eaf7ee;
  color: #175c37;
}

.error {
  background: #fff0ef;
  color: #b42318;
}

@media (max-width: 650px) {
  .campos {
    grid-template-columns: 1fr;
  }
}
</style>
