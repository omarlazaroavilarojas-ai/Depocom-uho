
<script setup>
import { ref, watch } from 'vue'

import {
  obtenerHistorialSolicitud,
} from '../api/historial'

const props = defineProps({
  solicitudId: {
    type: Number,
    required: true,
  },
})

const eventos = ref([])
const cargando = ref(false)
const error = ref('')

async function cargarHistorial() {
  cargando.value = true
  error.value = ''

  try {
    eventos.value = await obtenerHistorialSolicitud(
      props.solicitudId
    )
  } catch (err) {
    error.value = err.message
  } finally {
    cargando.value = false
  }
}

watch(
  () => props.solicitudId,
  cargarHistorial,
  { immediate: true }
)
</script>

<template>
  <section class="historial">
    <div class="cabecera">
      <h4>Historial de la solicitud</h4>

      <button
        type="button"
        @click="cargarHistorial"
      >
        Actualizar
      </button>
    </div>

    <p v-if="cargando">
      Cargando historial...
    </p>

    <p v-else-if="error" class="error">
      {{ error }}
    </p>

    <p v-else-if="eventos.length === 0">
      No hay eventos registrados.
    </p>

    <ol v-else class="eventos">
      <li
        v-for="evento in eventos"
        :key="evento.id"
        class="evento"
      >
        <strong>{{ evento.accion_nombre }}</strong>

        <p>{{ evento.descripcion }}</p>

        <small>
          {{ evento.usuario_nombre }}
          —
          {{
            new Date(evento.fecha).toLocaleString()
          }}
        </small>
      </li>
    </ol>
  </section>
</template>

<style scoped>
.historial {
  margin-top: 18px;
  padding: 16px;
  background: #f2f6fa;
  border-radius: 8px;
}

.cabecera {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

h4 {
  color: #123b5d;
}

button {
  padding: 8px 12px;
  background: white;
  color: #123b5d;
  border: 1px solid #123b5d;
  border-radius: 8px;
  cursor: pointer;
}

.eventos {
  padding-left: 22px;
}

.evento {
  margin-top: 14px;
  padding-bottom: 12px;
  border-bottom: 1px solid #d7e0e8;
}

.evento p {
  margin: 8px 0;
}

.evento small {
  color: #536879;
}

.error {
  color: #b42318;
}
</style>
