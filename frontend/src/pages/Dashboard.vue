<script setup>
import { ref, watch, onMounted } from "vue";

import { useApiStore } from "@/stores/api";
import { useAuthStore } from "@/stores/auth";
import DataTable from "@/components/data-table/DataTable.vue";
import { columns } from "@/components/data-table/columns";
import { Button } from "@/components/ui/button";
import Container from "@/components/Container.vue";

const api = useApiStore();
const auth = useAuthStore();
const rows = ref([]);
const totalCount = ref(0);
const error = ref("");

const pageIndex = ref(0);
const pageSize = ref(10);

const search = ref("");
const status = ref("");
const category = ref("");
const mine = ref(false); // My requests toggle

// Stats
const stats = ref({ total: 0, pending: 0, approved: 0, in_progress: 0, mine: 0 });

async function fetchStats() {
  if (auth.role === "submitter") {
    try {
      const mineData = await api.listRequests({ mine: "true", page_size: 1 });
      stats.value.mine = mineData?.count ?? 0;
    } catch (e) {
      console.error("Failed to load mine count", e);
    }
    return;
  }

  try {
    stats.value = await api.getStats();
  } catch (e) {
    console.error("Failed to load stats", e);
  }
}

async function fetchPage() {
  try {
    error.value = "";
    // DRF PageNumberPagination uses 1-based page numbers
    const data = await api.listRequests({
      page: pageIndex.value + 1,
      page_size: pageSize.value,
      q: search.value,
      status: status.value,
      category: category.value,
      mine: mine.value ? "true" : undefined,
    });
    rows.value = data?.results ?? [];
    totalCount.value = data?.count ?? 0;
  } catch (e) {
    error.value = e.message;
  }
}

function onPaginationChange(next) {
  // Reset to first page when page size changes
  if (next.pageSize !== pageSize.value) {
    pageIndex.value = 0;
    pageSize.value = next.pageSize;
  } else {
    pageIndex.value = next.pageIndex;
  }
}

watch([pageIndex, pageSize], fetchPage);
watch([search, status, category, mine], () => {
  pageIndex.value = 0; // Reset to page 1 on filter change
  fetchPage();
});
onMounted(() => {
  fetchPage();
  fetchStats();
});
</script>

<template>
  <Container>
    <section class="space-y-6 h-full">
      <!-- Header & New Request Button -->
      <div class="flex items-center justify-between space-y-2">
        <div>
          <h2 class="text-2xl font-bold tracking-tight">Welcome back!</h2>
          <p class="text-muted-foreground">Here's an overview of the latest project requests.</p>
        </div>
        <div class="flex items-center space-x-2">
          <RouterLink v-if="auth.role === 'submitter'" :to="{ name: 'request-new' }">
            <Button>New Request</Button>
          </RouterLink>
        </div>
      </div>

      <!-- Stat Tiles -->
      <div v-if="auth.role !== 'submitter'" class="grid gap-4 md:grid-cols-4">
        <div class="rounded-xl border bg-card text-card-foreground shadow-sm p-4">
          <h3 class="tracking-tight text-sm font-medium">Total Requests</h3>
          <p class="text-2xl font-bold mt-2">{{ stats.total }}</p>
        </div>
        <div class="rounded-xl border bg-card text-card-foreground shadow-sm p-4">
          <h3 class="tracking-tight text-sm font-medium">Pending</h3>
          <p class="text-2xl font-bold mt-2">{{ stats.pending }}</p>
        </div>
        <div class="rounded-xl border bg-card text-card-foreground shadow-sm p-4">
          <h3 class="tracking-tight text-sm font-medium">Approved</h3>
          <p class="text-2xl font-bold mt-2">{{ stats.approved }}</p>
        </div>
        <div class="rounded-xl border bg-card text-card-foreground shadow-sm p-4">
          <h3 class="tracking-tight text-sm font-medium">In Progress</h3>
          <p class="text-2xl font-bold mt-2">{{ stats.in_progress }}</p>
        </div>
      </div>

      <!-- My Requests Toggle -->
      <div class="flex gap-2 border-b" v-if="auth.role === 'submitter'">
        <button
          class="px-4 py-2 text-sm font-medium border-b-2 transition-colors cursor-pointer"
          :class="
            !mine
              ? 'border-primary text-foreground'
              : 'border-transparent text-muted-foreground hover:text-foreground'
          "
          @click="mine = false"
        >
          All Requests
        </button>
        <button
          class="px-4 py-2 text-sm font-medium border-b-2 transition-colors cursor-pointer"
          :class="
            mine
              ? 'border-primary text-foreground'
              : 'border-transparent text-muted-foreground hover:text-foreground'
          "
          @click="mine = true"
        >
          My Requests ({{ stats.mine }})
        </button>
      </div>

      <pre v-if="error">{{ error }}</pre>
      <DataTable
        v-else
        :columns="columns"
        :data="rows"
        :row-count="totalCount"
        :page-index="pageIndex"
        :page-size="pageSize"
        :search="search"
        :status="status"
        :category="category"
        @update:search="search = $event"
        @update:status="status = $event"
        @update:category="category = $event"
        @update:pagination="onPaginationChange"
      />
    </section>
  </Container>
</template>
