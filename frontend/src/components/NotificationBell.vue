<script setup>
import { onMounted, onUnmounted, watch } from "vue";
import { useRouter, useRoute } from "vue-router";
import { BellIcon } from "@lucide/vue";

import { useAuthStore } from "@/stores/auth";
import { useRealtimeStore } from "@/stores/realtime";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

const auth = useAuthStore();
const realtime = useRealtimeStore();
const router = useRouter();
const route = useRoute();

// Connect/disconnect SSE based on auth state
onMounted(() => {
  if (auth.isAuthenticated) {
    realtime.connect();
  }
});

onUnmounted(() => {
  realtime.disconnect();
});

watch(
  () => auth.isAuthenticated,
  (isAuth) => {
    if (isAuth) {
      realtime.connect();
    } else {
      realtime.disconnect();
    }
  },
);

function handleNotificationClick(notification) {
  realtime.markAsRead(notification.id);
  const targetId = notification.data.request_id;

  if (targetId) {
    if (route.name === "request-detail" && route.params.id === targetId) {
      // Already on this page, emit a soft refresh event
      window.dispatchEvent(new CustomEvent("refresh-request-data"));
    } else {
      router.push({
        name: "request-detail",
        params: { id: targetId },
      });
    }
  }
}

function formatTime(isoString) {
  const date = new Date(isoString);
  const now = new Date();
  const diffMs = now - date;
  const diffMin = Math.floor(diffMs / 60000);
  const diffHr = Math.floor(diffMs / 3600000);

  if (diffMin < 1) return "just now";
  if (diffMin < 60) return `${diffMin}m ago`;
  if (diffHr < 24) return `${diffHr}h ago`;
  return date.toLocaleDateString();
}

// https://emojidb.org/update-emojis
const EVENT_ICONS = {
  proposal_created: "📝",
  proposal_updated: "🔔",
  comment_added: "💬",
  proposal_resubmitted: "📋",
};
</script>

<template>
  <DropdownMenu>
    <DropdownMenuTrigger as-child>
      <Button id="notification-bell" variant="ghost" class="relative h-8 w-8 rounded-full">
        <BellIcon class="h-4 w-4" />
        <span
          v-if="realtime.unreadCount > 0"
          class="absolute -top-0.5 -right-0.5 flex h-4 min-w-4 items-center justify-center rounded-full bg-destructive/20 px-1 text-[10px] font-bold text-destructive-foreground"
        >
          {{ realtime.unreadCount > 99 ? "99+" : realtime.unreadCount }}
        </span>
      </Button>
    </DropdownMenuTrigger>

    <DropdownMenuContent class="w-80" align="end">
      <DropdownMenuLabel class="flex items-center justify-between">
        <span>Notifications</span>
        <button
          v-if="realtime.unreadCount > 0"
          class="text-xs font-normal text-muted-foreground hover:text-foreground cursor-pointer"
          @click.stop="realtime.markAllAsRead()"
        >
          Mark all as read
        </button>
      </DropdownMenuLabel>
      <DropdownMenuSeparator />

      <!-- Empty state -->
      <div
        v-if="realtime.notifications.length === 0"
        class="py-6 text-center text-sm text-muted-foreground"
      >
        No notifications yet
      </div>

      <!-- Notification list (scrollable) -->
      <div class="max-h-80 overflow-y-auto">
        <DropdownMenuItem
          v-for="n in realtime.notifications.slice(0, 20)"
          :key="n.id"
          class="flex cursor-pointer items-start gap-3 p-3"
          :class="{ 'bg-muted/50': !n.read }"
          @click="handleNotificationClick(n)"
        >
          <span class="mt-0.5 text-base">{{ EVENT_ICONS[n.type] || "📌" }}</span>
          <div class="flex-1 min-w-0">
            <p class="text-sm leading-tight">
              <span class="font-medium">{{ n.data.actor_name }}</span>
              {{ " " }}
              <span class="text-muted-foreground">{{
                realtime.getActionLabel(n.data.action)
              }}</span>
            </p>
            <p v-if="n.data.title" class="mt-0.5 truncate text-xs text-muted-foreground">
              {{ n.data.title }}
            </p>
            <p class="mt-1 text-xs text-muted-foreground/70">
              {{ formatTime(n.receivedAt) }}
            </p>
          </div>
          <span v-if="!n.read" class="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-primary" />
        </DropdownMenuItem>
      </div>

      <!-- Footer -->
      <template v-if="realtime.notifications.length > 0">
        <DropdownMenuSeparator />
        <div class="p-2 text-center">
          <button
            class="text-xs text-muted-foreground hover:text-foreground cursor-pointer"
            @click.stop="realtime.clearAll()"
          >
            Clear all notifications
          </button>
        </div>
      </template>
    </DropdownMenuContent>
  </DropdownMenu>
</template>
