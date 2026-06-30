import { defineStore } from "pinia";

import { useAuthStore } from "@/stores/auth";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

// Error class for HTTP status and the backend body
export class ApiError extends Error {
  constructor(message, status, data) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.data = data || {};
    this.fields = data?.fields;
  }
}

export const useApiStore = defineStore("api", () => {
  const auth = useAuthStore();

  // Core request fetch
  async function _request(path, { method = "GET", body, params } = {}) {
    const url = new URL(API_BASE + path);
    if (params) {
      for (const [key, value] of Object.entries(params)) {
        if (value !== undefined && value !== null && value !== "") {
          url.searchParams.set(key, value);
        }
      }
    }

    const headers = {};
    if (body !== undefined) headers["Content-Type"] = "application/json";
    if (auth.access) headers.Authorization = `Bearer ${auth.access}`;

    const res = await fetch(url, {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });

    // Unauthorized
    if (res.status === 401) {
      auth.logout();
      throw new ApiError("Session expired, please sign in again.", 401, {});
    }

    // Success check
    const data = res.status === 204 ? null : await res.json().catch(() => null);
    if (!res.ok) {
      throw new ApiError(data?.detail || "Request failed", res.status, data);
    }
    return data;
  }

  // Endpoints
  const listRequests = (params) => _request("/api/requests/", { params });

  return {
    listRequests,
  };
});
