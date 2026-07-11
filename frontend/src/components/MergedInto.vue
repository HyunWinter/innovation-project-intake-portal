<script setup>
// Searchable dropdown for picking a request to merge the current one into.
// TODO: Make a separate backend API for fetching only 4 requests
// TODO: Make backend only fetch requests excluding the current one and mergeable (currently done in frontend)
// TODO: Make request searchable by ID as well (because there can be more than 4 requests with the same title)
// TODO: Add filters

import { ref, computed, onMounted } from "vue";
import { useApiStore } from "@/stores/api";
import {
  ComboboxRoot,
  ComboboxAnchor,
  ComboboxTrigger,
  ComboboxInput,
  ComboboxPortal,
  ComboboxContent,
  ComboboxViewport,
  ComboboxEmpty,
  ComboboxItem,
  ComboboxItemIndicator,
} from "reka-ui";

// props and emits
const props = defineProps({
  modelValue: { type: String, default: "" },
  excludeId: { type: String, default: "" },
});
const emit = defineEmits(["update:modelValue"]);

const api = useApiStore();
const options = ref([]);
const loadError = ref("");

const selected = computed({
  get: () => props.modelValue || null,
  set: (v) => emit("update:modelValue", v ?? ""),
});

const selectedLabel = computed(() => {
  const match = options.value.find((r) => r.id === props.modelValue);
  return match ? match.title : "";
});

// Never the current one
onMounted(async () => {
  try {
    // Could also be A categories as well
    // But merge is only allowed from B
    const data = await api.listRequests({ category: "B" });
    const rows = data?.results ?? data ?? [];
    options.value = rows.filter((r) => r.id !== props.excludeId);
  } catch (e) {
    loadError.value = e.message || "Failed to load projects";
  }
});
</script>

<template>
  <ComboboxRoot v-model="selected">
    <ComboboxAnchor as-child>
      <ComboboxTrigger as-child>
        <button
          type="button"
          class="flex h-9 w-full items-center justify-between rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
        >
          <span
            class="truncate"
            :class="selectedLabel ? 'text-foreground' : 'text-muted-foreground'"
          >
            {{ selectedLabel || "Select a project..." }}
          </span>
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            class="ml-2 shrink-0 opacity-50"
          >
            <path d="m7 15 5 5 5-5" />
            <path d="m7 9 5-5 5 5" />
          </svg>
        </button>
      </ComboboxTrigger>
    </ComboboxAnchor>

    <ComboboxPortal>
      <ComboboxContent
        position="popper"
        :side-offset="4"
        class="z-50 w-[var(--reka-popper-anchor-width)] min-w-[12rem] rounded-md border bg-popover text-popover-foreground shadow-md"
      >
        <div class="flex items-center border-b px-3">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="14"
            height="14"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            class="mr-2 shrink-0 opacity-50"
          >
            <circle cx="11" cy="11" r="8" />
            <path d="m21 21-4.3-4.3" />
          </svg>
          <ComboboxInput
            placeholder="Search projects..."
            class="h-9 w-full bg-transparent text-sm outline-none placeholder:text-muted-foreground"
          />
        </div>

        <ComboboxViewport class="max-h-60 overflow-y-auto p-1">
          <ComboboxEmpty class="py-4 text-center text-sm text-muted-foreground">
            No project found.
          </ComboboxEmpty>

          <ComboboxItem
            v-for="option in options"
            :key="option.id"
            :value="option.id"
            :text-value="option.title"
            class="relative flex cursor-default select-none items-center rounded-sm py-1.5 pl-2 pr-8 text-sm outline-none data-[highlighted]:bg-accent data-[highlighted]:text-accent-foreground"
          >
            <div class="flex flex-col overflow-hidden">
              <span class="truncate">{{ option.title }}</span>
              <span class="text-xs text-muted-foreground">{{ option.status_label }}</span>
            </div>
            <ComboboxItemIndicator class="absolute right-2 flex items-center">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2.5"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <polyline points="20 6 9 17 4 12" />
              </svg>
            </ComboboxItemIndicator>
          </ComboboxItem>
        </ComboboxViewport>
      </ComboboxContent>
    </ComboboxPortal>
  </ComboboxRoot>
</template>
