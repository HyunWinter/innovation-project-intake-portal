<script setup>
import { useRouter } from "vue-router";

import { useAuthStore } from "@/stores/auth";

const auth = useAuthStore();
const router = useRouter();

function logout() {
  auth.logout();
  router.push({ name: "login" });
}
</script>

<template>
  <nav class="flex gap-x-6">
    <RouterLink :to="{ name: 'dashboard' }">Dashboard</RouterLink>
    <RouterLink v-if="auth.role === 'submitter'" :to="{ name: 'request-new' }"
      >New Request</RouterLink
    >
    <span>{{ auth.name }} ({{ auth.role }})</span>
    <button type="button" @click="logout">Logout</button>
  </nav>
</template>
