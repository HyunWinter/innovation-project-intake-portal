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

// A stateless store for handling API requests
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
      let msg = data?.detail;
      if (!msg && data && typeof data === "object") {
        const firstKey = Object.keys(data)[0];
        if (firstKey && Array.isArray(data[firstKey])) {
          msg = `${data[firstKey][0]}`;
        } else if (firstKey && typeof data[firstKey] === "string") {
          msg = `${data[firstKey]}`;
        }
      }
      throw new ApiError(msg || "Request failed", res.status, data);
    }
    return data;
  }

  // Endpoints
  const listRequests = (params) => _request("/api/requests/", { params });
  const getRequest = (id) => _request(`/api/requests/${id}/`);
  const createRequest = (data) => _request("/api/requests/", { method: "POST", body: data });
  const resubmitRequest = (id, data) =>
    _request(`/api/requests/${id}/`, { method: "PATCH", body: data });
  // committee-decision, presentation, funding-decision, execution, etc...
  const runTransition = (id, endpoint, body) =>
    _request(`/api/requests/${id}/${endpoint}/`, { method: "POST", body });
  const addComment = (id, text) =>
    _request(`/api/requests/${id}/comments/`, {
      method: "POST",
      body: { action: "comment", body: text },
    });
  const getStats = () => _request("/api/requests/stats/");

  // Drafts (Singleton)
  const getDraft = () => _request("/api/draft/");
  const saveDraft = (data) => _request("/api/draft/", { method: "PUT", body: data });
  const deleteDraft = () => _request("/api/draft/", { method: "DELETE" });

  return {
    listRequests,
    getRequest,
    createRequest,
    resubmitRequest,
    runTransition,
    addComment,
    getStats,
    getDraft,
    saveDraft,
    deleteDraft,
  };
});
