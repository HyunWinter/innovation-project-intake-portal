/**
 * Realtime SSE store
 *
 * Connects to the backend SSE stream on login
 * Receives real-time events: proposal_created, proposal_updated, comment_added, proposal_resubmitted
 * Maintains a notification list for the bell icon in the navbar
 */
import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { useAuthStore } from "@/stores/auth";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";
const MAX_NOTIFICATIONS = 50;

// Action labels
const ACTION_LABELS = {
  create: "submitted a new proposal",
  proceed_independently: "approved (proceed independently)",
  collaboration_recommended: "approved (collaboration recommended)",
  hold: "placed on hold",
  search_insufficient: "requested more research",
  reject: "rejected",
  request_presentation: "requested a presentation",
  combine_existing: "merged with existing",
  enhance_search: "requested enhanced search",
  schedule: "scheduled a presentation",
  advanced: "advanced after presentation",
  not_advanced: "rejected after presentation",
  go: "approved funding",
  no_go: "denied funding",
  start: "started execution",
  complete: "marked as completed",
  resume: "resumed from hold",
  comment: "added a comment",
  resubmit: "resubmitted the proposal",
};

export const useRealtimeStore = defineStore("realtime", () => {
  const auth = useAuthStore();

  /** @type {import('vue').Ref<EventSource|null>} */
  const source = ref(null);
  const connected = ref(false);
  const initialized = ref(false);

  /** @type {import('vue').Ref<Array<{id: string, type: string, data: object, read: boolean, receivedAt: string}>>} */
  const notifications = ref([]);

  const unreadCount = computed(() => notifications.value.filter((n) => !n.read).length);

  // Connection management
  function connect() {
    if (source.value || !auth.access) return;

    const url = `${API_BASE}/api/events/stream/?token=${auth.access}`;
    const es = new EventSource(url);

    // Open connection and fetch persisted history
    es.onopen = () => {
      connected.value = true;
      if (!initialized.value) {
        loadNotifications();
        initialized.value = true;
      }
    };

    es.onerror = () => {
      connected.value = false;
      // disconnect when unauthenticated
      if (!auth.access) {
        disconnect();
      }
    };

    // Listen for each event type
    const eventTypes = [
      "proposal_created",
      "proposal_updated",
      "comment_added",
      "proposal_resubmitted",
    ];

    for (const type of eventTypes) {
      es.addEventListener(type, (e) => {
        const data = JSON.parse(e.data);

        // Only notify if not from self
        if (auth.claims?.user_id && data.actor_id === auth.claims.user_id) {
          return;
        }

        // Add to front of list
        const notification = {
          id: data.id || `${Date.now()}-${Math.random().toString(36).slice(2, 7)}`, // Fallback ID
          type,
          data,
          read: false,
          receivedAt: new Date().toISOString(),
        };

        // Prevent duplicates
        if (!notifications.value.find((n) => n.id === notification.id)) {
          notifications.value.unshift(notification);

          // Cap the list
          if (notifications.value.length > MAX_NOTIFICATIONS) {
            notifications.value = notifications.value.slice(0, MAX_NOTIFICATIONS);
          }
        }
      });
    }

    source.value = es;
  }

  function disconnect() {
    if (source.value) {
      source.value.close();
      source.value = null;
      connected.value = false;
      initialized.value = false;
    }
  }

  // Notification actions

  async function loadNotifications() {
    if (!auth.access) return;

    try {
      const res = await fetch(`${API_BASE}/api/events/notifications/?unread=true`, {
        headers: { Authorization: `Bearer ${auth.access}` },
      });
      if (!res.ok) return;

      const data = await res.json();

      // Map API format to store format
      notifications.value = data.map((n) => ({
        id: n.id,
        type: n.event_type,
        data: {
          request_id: n.request_ref,
          title: n.title,
          action: n.action,
          from_status: n.from_status,
          to_status: n.to_status,
          actor_name: n.actor_name,
          actor_id: n.actor,
        },
        read: n.read,
        receivedAt: n.created_at,
      }));
    } catch (err) {
      console.error("Failed to load notifications", err);
    }
  }

  async function markAsRead(id) {
    const n = notifications.value.find((n) => n.id === id);
    if (!n || n.read) return;

    // Immediately remove from the UI (Inbox pattern)
    notifications.value = notifications.value.filter((n) => n.id !== id);

    try {
      await fetch(`${API_BASE}/api/events/notifications/${id}/read/`, {
        method: "PATCH",
        headers: { Authorization: `Bearer ${auth.access}` },
      });
    } catch (err) {
      console.error("Failed to mark read", err);
    }
  }

  async function markAllAsRead() {
    // Clear array immediately
    notifications.value = [];

    try {
      await fetch(`${API_BASE}/api/events/notifications/read-all/`, {
        method: "POST",
        headers: { Authorization: `Bearer ${auth.access}` },
      });
    } catch (err) {
      console.error("Failed to mark all read", err);
    }
  }

  async function clearAll() {
    notifications.value = [];

    try {
      await fetch(`${API_BASE}/api/events/notifications/clear-all/`, {
        method: "POST",
        headers: { Authorization: `Bearer ${auth.access}` },
      });
    } catch (err) {
      console.error("Failed to clear all", err);
    }
  }

  function getActionLabel(action) {
    return ACTION_LABELS[action] || action;
  }

  return {
    connected,
    notifications,
    unreadCount,
    connect,
    disconnect,
    markAsRead,
    markAllAsRead,
    clearAll,
    getActionLabel,
  };
});
