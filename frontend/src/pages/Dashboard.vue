<script setup>
import { ref, onMounted } from "vue";

import { useApiStore } from "@/stores/api";

const api = useApiStore();
const data = ref(null);
const error = ref("");

onMounted(async () => {
  try {
    data.value = await api.listRequests();
  } catch (e) {
    error.value = e.message;
  }
});
</script>

<template>
  <pre v-if="error">{{ error }}</pre>
  <div v-else-if="data?.results" class="grid gap-6">
    <div v-for="request in data.results">{{ request }}</div>
  </div>
</template>
