<script setup>
import { X } from "@lucide/vue";
import { computed } from "vue";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

const props = defineProps({
  search: { type: String, required: false, default: "" },
  status: { type: String, required: false, default: "" },
  category: { type: String, required: false, default: "" },
});

const emit = defineEmits(["update:search", "update:status", "update:category"]);

const statuses = [
  { value: "pending", label: "Pending" },
  { value: "under_review", label: "Under review" },
  { value: "approved", label: "Approved" },
  { value: "in_progress", label: "In progress" },
  { value: "on_hold", label: "On hold" },
  { value: "completed", label: "Completed" },
  { value: "rejected", label: "Rejected" },
  { value: "merged", label: "Merged" },
];

const categories = [
  { value: "A", label: "A - No funding" },
  { value: "B", label: "B - Funding required" },
];

const isFiltered = computed(() => props.search || props.status || props.category);

function resetFilters() {
  emit("update:search", "");
  emit("update:status", "");
  emit("update:category", "");
}
</script>

<template>
  <div class="flex items-center justify-between">
    <div class="flex flex-1 items-center space-x-2">
      <Input
        placeholder="Search requests..."
        :model-value="search"
        class="h-8 w-[150px] lg:w-[250px]"
        @input="emit('update:search', $event.target.value)"
      />
      <Select
        :model-value="status || undefined"
        @update:model-value="emit('update:status', $event)"
      >
        <SelectTrigger class="h-8 w-[150px]">
          <SelectValue placeholder="Status" />
        </SelectTrigger>
        <SelectContent position="popper" align="start">
          <SelectItem v-for="s in statuses" :key="s.value" :value="s.value">
            {{ s.label }}
          </SelectItem>
        </SelectContent>
      </Select>
      <Select
        :model-value="category || undefined"
        @update:model-value="emit('update:category', $event)"
      >
        <SelectTrigger class="h-8 w-[150px]">
          <SelectValue placeholder="Category" />
        </SelectTrigger>
        <SelectContent position="popper" align="start">
          <SelectItem v-for="c in categories" :key="c.value" :value="c.value">
            {{ c.label }}
          </SelectItem>
        </SelectContent>
      </Select>

      <Button v-if="isFiltered" variant="ghost" class="h-8 px-2 lg:px-3" @click="resetFilters">
        Reset
        <X class="ml-2 h-4 w-4" />
      </Button>
    </div>
  </div>
</template>
