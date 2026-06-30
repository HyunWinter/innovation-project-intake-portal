import { defineStore } from "pinia";
import { ref, computed } from "vue";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

// JWT decoder for role and name parameters
function decodeJwt(token) {
  try {
    const payload = token.split(".")[1].replace(/-/g, "+").replace(/_/g, "/");
    return JSON.parse(atob(payload));
  } catch {
    return null;
  }
}

export const useAuthStore = defineStore("auth", () => {
  const access = ref(localStorage.getItem("access") || "");
  const refresh = ref(localStorage.getItem("refresh") || "");

  const claims = computed(() => (access.value ? decodeJwt(access.value) : null));
  const isAuthenticated = computed(() => !!access.value);
  const role = computed(() => claims.value?.role || null);
  const name = computed(() => claims.value?.name || "");

  function setTokens(a, r) {
    access.value = a;
    refresh.value = r;
    localStorage.setItem("access", a);
    localStorage.setItem("refresh", r);
  }

  async function login(email, password) {
    const res = await fetch(`${API_BASE}/api/token/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) throw new Error("Invalid email or password");
    const data = await res.json();
    setTokens(data.access, data.refresh);
  }

  function logout() {
    access.value = "";
    refresh.value = "";
    localStorage.removeItem("access");
    localStorage.removeItem("refresh");
  }

  return { access, refresh, claims, isAuthenticated, role, name, login, logout };
});
