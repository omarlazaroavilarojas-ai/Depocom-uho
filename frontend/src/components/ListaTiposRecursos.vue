
<script setup>
defineProps({
  tiposRecursos: {
    type: Array,
    required: true,
  },
})
</script>

<template>
  <article class="tarjeta">
    <h3>Tipos de recursos</h3>

    <p v-if="tiposRecursos.length === 0">
      No hay tipos de recursos registrados.
    </p>

    <ul v-else>
      <li
        v-for="tipo in tiposRecursos"
        :key="tipo.id"
      >
        {{ tipo.nombre }}
      </li>
    </ul>
  </article>
</template>

<style scoped>
.tarjeta {
  background-color: #f5f8fb;
  border: 1px solid #d7e0e8;
  border-radius: 12px;
  padding: 24px;
  color: #18364b;
}

.tarjeta h3 {
  margin-top: 0;
}

ul {
  padding-left: 20px;
}

li {
  margin-bottom: 14px;
}
</style>
