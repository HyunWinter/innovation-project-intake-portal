<script setup>
import { useRoute } from "vue-router";

import Navbar from "@/components/Navbar.vue";
import { useAuthStore } from "@/stores/auth";

const auth = useAuthStore();
const route = useRoute();
</script>

<template>
  <header
    v-if="auth.isAuthenticated && route.name !== 'login'"
    class="sticky flex top-0 z-50 w-full shrink-0 justify-center border-b border-dashed backdrop-blur-sm bg-background/60 h-16"
  >
    <Navbar />
  </header>
  <router-view />
</template>
