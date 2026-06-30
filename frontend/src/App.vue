<script setup>
import { useRoute } from "vue-router";

import Navbar from "@/components/Navbar.vue";
import { useAuthStore } from "@/stores/auth";

const auth = useAuthStore();
const route = useRoute();
</script>

<template>
  <Navbar v-if="auth.isAuthenticated && route.name !== 'login'" />
  <router-view />
</template>
