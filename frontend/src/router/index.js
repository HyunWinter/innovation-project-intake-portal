import { createRouter, createWebHistory } from "vue-router";

import { useAuthStore } from "@/stores/auth";

// Page routes
// Often with CMS, specific pages can be defined in the backend instead of Frontend
const routes = [
  {
    path: "/login",
    name: "login",
    component: () => import("@/pages/Login.vue"),
    meta: { public: true },
  },
  {
    path: "/",
    name: "dashboard",
    component: () => import("@/pages/Dashboard.vue"),
  },
  {
    path: "/requests/new",
    name: "request-new",
    component: () => import("@/pages/RequestForm.vue"),
  },
  {
    path: "/requests/:id",
    name: "request-detail",
    component: () => import("@/pages/RequestReviewScreen.vue"),
    props: true,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Send unauthenticated users back to login
router.beforeEach((to) => {
  const auth = useAuthStore();
  if (!to.meta.public && !auth.isAuthenticated) {
    return { name: "login", query: { next: to.fullPath } };
  }

  // Non-submitters should not access the New Request form
  if (to.name === "request-new" && auth.role !== "submitter") {
    return { name: "dashboard" };
  }
});

export default router;
