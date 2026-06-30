<script setup>
import { ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import { useAuthStore } from "@/stores/auth";

const auth = useAuthStore();
const router = useRouter();
const route = useRoute();

const email = ref("");
const password = ref("");
const error = ref("");
const loading = ref(false);

async function submit() {
  error.value = "";
  loading.value = true;
  try {
    await auth.login(email.value, password.value);
    // Return to next or dashboard
    router.push(route.query.next || { name: "dashboard" });
  } catch (e) {
    error.value = e.message || "Login failed";
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <form @submit.prevent="submit" class="flex flex-col">
    <h1>Innovation Project Intake Portal</h1>

    <label for="email">Email</label>
    <input id="email" v-model="email" type="email" required autocomplete="email" />

    <label for="password">Password</label>
    <input
      id="password"
      v-model="password"
      type="password"
      required
      autocomplete="current-password"
    />

    <p v-if="error">{{ error }}</p>

    <button type="submit" :disabled="loading">
      {{ loading ? "Signing in..." : "Sign in" }}
    </button>
  </form>
</template>
