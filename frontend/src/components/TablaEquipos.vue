
<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  equipos: {
    type: Array,
    required: true,
  },
  puedeEditar: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['editar-equipo'])

const busqueda = ref('')
const tipoSeleccionado = ref('todos')
const equipoDetalle = ref(null)

const tiposDisponibles = computed(() => {
  const mapa = new Map()

  for (const equipo of props.equipos) {
    mapa.set(
      equipo.tipo_recurso,
      equipo.tipo_recurso_nombre
    )
  }

  return Array.from(mapa, ([id, nombre]) => ({
    id,
    nombre,
  }))
})

const equiposFiltrados = computed(() => {
  const texto = busqueda.value.trim().toLowerCase()

  return props.equipos.filter((equipo) => {
    const coincideTexto = [
      equipo.no_inventario,
      equipo.marca,
      equipo.modelo,
    ].some((valor) =>
      String(valor ?? '').toLowerCase().includes(texto)
    )

    const coincideTipo =
      tipoSeleccionado.value === 'todos' ||
      String(equipo.tipo_recurso) === tipoSeleccionado.value

    return coincideTexto && coincideTipo
  })
})

function limpiarFiltros() {
  busqueda.value = ''
  tipoSeleccionado.value = 'todos'
}

function verDetalles(equipo) {
  equipoDetalle.value = equipo
}
</script>

<template>
  <section class="tabla-contenedor">
    <h2>Equipos registrados</h2>

    <div class="filtros">
      <input
        v-model="busqueda"
        type="search"
        placeholder="Buscar inventario, marca o modelo..."
        aria-label="Buscar equipos"
      />

      <select
        v-model="tipoSeleccionado"
        aria-label="Filtrar por tipo"
      >
        <option value="todos">Todos los tipos</option>

        <option
          v-for="tipo in tiposDisponibles"
          :key="tipo.id"
          :value="String(tipo.id)"
        >
          {{ tipo.nombre }}
        </option>
      </select>

      <button type="button" @click="limpiarFiltros">
        Limpiar filtros
      </button>
    </div>

    <p class="contador">
      Mostrando {{ equiposFiltrados.length }}
      de {{ equipos.length }} equipos
    </p>

    <div class="tabla-scroll">
      <table>
        <thead>
          <tr>
            <th>Inventario</th>
            <th>Tipo</th>
            <th>Marca</th>
            <th>Modelo</th>
            <th>Serie</th>
            <th>Departamento</th>
            <th>Acciones</th>
          </tr>
        </thead>

        <tbody>
          <tr
            v-for="equipo in equiposFiltrados"
            :key="equipo.id"
          >
            <td>{{ equipo.no_inventario }}</td>
            <td>{{ equipo.tipo_recurso_nombre }}</td>
            <td>{{ equipo.marca || '—' }}</td>
            <td>{{ equipo.modelo || '—' }}</td>
            <td>{{ equipo.no_serie || '—' }}</td>
            <td>{{ equipo.departamento_nombre || 'Sin asignar' }}</td>
            <td>
              <div class="acciones">
                <button
                  type="button"
                  @click="verDetalles(equipo)"
                >
                  Detalles
                </button>

                <button
                  v-if="puedeEditar"
                  type="button"
                  @click="emit('editar-equipo', equipo)"
                >
                  Editar
                </button>
              </div>
            </td>
          </tr>

          <tr v-if="equiposFiltrados.length === 0">
            <td colspan="7" class="vacio">
              No hay equipos que coincidan con los filtros.
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="equipoDetalle" class="detalle">
      <div class="detalle-cabecera">
        <h3>Detalles del equipo</h3>
        <button
          type="button"
          @click="equipoDetalle = null"
        >
          Cerrar
        </button>
      </div>

      <p><strong>Inventario:</strong> {{ equipoDetalle.no_inventario }}</p>
      <p><strong>Tipo:</strong> {{ equipoDetalle.tipo_recurso_nombre }}</p>
      <p><strong>Marca:</strong> {{ equipoDetalle.marca || '—' }}</p>
      <p><strong>Modelo:</strong> {{ equipoDetalle.modelo || '—' }}</p>
      <p><strong>Serie:</strong> {{ equipoDetalle.no_serie || '—' }}</p>
      <p>
        <strong>Departamento:</strong>
        {{ equipoDetalle.departamento_nombre || 'Sin asignar' }}
      </p>
    </div>
  </section>
</template>

<style scoped>
.tabla-contenedor {
  margin-top: 36px;
  padding: 24px;
  background: white;
  border: 1px solid #d7e0e8;
  border-radius: 12px;
}

h2, h3 {
  color: #123b5d;
}

.filtros {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin: 20px 0;
}

.filtros input,
.filtros select {
  padding: 11px;
  border: 1px solid #ccd8e2;
  border-radius: 8px;
}

.filtros input {
  flex: 2;
  min-width: 200px;
}

.filtros select {
  flex: 1;
  min-width: 150px;
}

button {
  padding: 9px 12px;
  border: 1px solid #123b5d;
  border-radius: 7px;
  background: white;
  color: #123b5d;
  cursor: pointer;
}

.contador {
  color: #536879;
  font-size: 14px;
}

.tabla-scroll {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 13px 10px;
  border-bottom: 1px solid #e1e7ed;
  text-align: left;
}

th {
  background: #f2f6fa;
  color: #123b5d;
}

.acciones {
  display: flex;
  gap: 8px;
}

.vacio {
  text-align: center;
  padding: 30px;
  color: #536879;
}

.detalle {
  margin-top: 24px;
  padding: 20px;
  border: 1px solid #d7e0e8;
  border-radius: 10px;
  background: #f5f8fb;
}

.detalle-cabecera {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.detalle p {
  margin: 10px 0;
}

@media (max-width: 650px) {
  .tabla-contenedor {
    padding: 14px;
  }
}
</style>
