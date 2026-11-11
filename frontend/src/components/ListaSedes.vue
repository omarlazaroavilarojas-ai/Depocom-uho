
<script setup>
defineProps({
  sedes: {
    type: Array,
    required: true,
  },
})
</script>

<template>
  <article class="tarjeta">
    <h3>Sedes</h3>

    <p v-if="sedes.length === 0">
      No hay sedes registradas.
    </p>

    <ul v-else>
      <li v-for="sede in sedes" :key="sede.id">
        <strong>{{ sede.nombre }}</strong>
        <span>{{ sede.direccion }}</span>
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

li span {
  display: block;
  margin-top: 4px;
  font-size: 14px;
}
</style>
