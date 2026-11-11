
<script setup>
import { ref } from 'vue'

import {
  iniciarSesion,
  cerrarSesion,
} from '../api/sesion'

const props = defineProps({
  sesion: {
    type: Object,
    required: true,
  },
})

const emit = defineEmits(['actualizar-sesion'])

const usuario = ref('')
const contrasena = ref('')
const error = ref('')
const procesando = ref(false)

async function entrar() {
  error.value = ''
  procesando.value = true

  try {
    const datos = await iniciarSesion(
      usuario.value,
      contrasena.value
    )

    emit('actualizar-sesion', datos)

    contrasena.value = ''
  } catch (err) {
    error.value = err.message
  } finally {
    procesando.value = false
  }
}

async function salir() {
  error.value = ''
  procesando.value = true

  try {
    const datos = await cerrarSesion()
    emit('actualizar-sesion', datos)

    usuario.value = ''
    contrasena.value = ''
  } catch (err) {
    error.value = err.message
  } finally {
    procesando.value = false
  }
}
</script>

<template>
  <section class="panel">
    <template v-if="props.sesion.autenticado">
      <div class="fila">
        <div>
          <strong>
            Sesión: {{ props.sesion.usuario }}
          </strong>

          <p v-if="props.sesion.puede_crear_equipos">
            Registro de equipos habilitado.
          </p>

          <p v-else>
            Tu cuenta no tiene permiso para
            registrar equipos.
          </p>
        </div>

        <button
          type="button"
          :disabled="procesando"
          @click="salir"
        >
          Cerrar sesión
        </button>
      </div>
    </template>

    <template v-else>
      <h2>Iniciar sesión</h2>

      <form @submit.prevent="entrar">
        <div class="campos">
          <div class="campo">
            <label for="usuario">Usuario</label>

            <input
              id="usuario"
              v-model="usuario"
              autocomplete="username"
              required
            />
          </div>

          <div class="campo">
            <label for="contrasena">
              Contraseña
            </label>

            <input
              id="contrasena"
              v-model="contrasena"
              type="password"
              autocomplete="current-password"
              required
            />
          </div>
        </div>

        <button
          type="submit"
          :disabled="procesando"
        >
          {{ procesando ? 'Entrando...' : 'Entrar' }}
        </button>
      </form>
    </template>

    <p v-if="error" class="error" role="alert">
      {{ error }}
    </p>
  </section>
</template>

<style scoped>
.panel {
  margin-top: 24px;
  padding: 24px;
  background: #f5f8fb;
  border: 1px solid #d7e0e8;
  border-radius: 12px;
}

h2 {
  margin-top: 0;
  color: #123b5d;
}

.fila {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  flex-wrap: wrap;
}

.fila p {
  color: #536879;
}

.campos {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.campo {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
  min-width: 180px;
}

input {
  box-sizing: border-box;
  width: 100%;
  padding: 12px;
  border: 1px solid #ccd8e2;
  border-radius: 8px;
}

button {
  padding: 12px 20px;
  background: #123b5d;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error {
  color: #b42318;
  margin-top: 12px;
}
</style>
