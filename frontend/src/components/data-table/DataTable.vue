<script setup>
import {
  FlexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getSortedRowModel,
  useVueTable,
} from "@tanstack/vue-table";
import { ref } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();

import { valueUpdater } from "@/lib/utils";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import DataTablePagination from "./DataTablePagination.vue";
import DataTableToolbar from "./DataTableToolbar.vue";

const props = defineProps({
  columns: { type: Array, required: true },
  data: { type: Array, required: true },
  rowCount: { type: Number, required: false, default: 0 },
  pageIndex: { type: Number, required: false, default: 0 },
  pageSize: { type: Number, required: false, default: 10 },
  search: { type: String, required: false, default: "" },
  status: { type: String, required: false, default: "" },
  category: { type: String, required: false, default: "" },
});

const emit = defineEmits([
  "update:pagination",
  "update:search",
  "update:status",
  "update:category",
]);

const sorting = ref([]);
const columnFilters = ref([]);
const columnVisibility = ref({});
const rowSelection = ref({});

const table = useVueTable({
  get data() {
    return props.data;
  },
  get columns() {
    return props.columns;
  },
  get rowCount() {
    return props.rowCount;
  },
  state: {
    get sorting() {
      return sorting.value;
    },
    get columnFilters() {
      return columnFilters.value;
    },
    get columnVisibility() {
      return columnVisibility.value;
    },
    get rowSelection() {
      return rowSelection.value;
    },
    get pagination() {
      return { pageIndex: props.pageIndex, pageSize: props.pageSize };
    },
  },
  manualPagination: true,
  enableRowSelection: true,
  onSortingChange: (updaterOrValue) => valueUpdater(updaterOrValue, sorting),
  onColumnFiltersChange: (updaterOrValue) => valueUpdater(updaterOrValue, columnFilters),
  onColumnVisibilityChange: (updaterOrValue) => valueUpdater(updaterOrValue, columnVisibility),
  onRowSelectionChange: (updaterOrValue) => valueUpdater(updaterOrValue, rowSelection),
  onPaginationChange: (updaterOrValue) => {
    const current = { pageIndex: props.pageIndex, pageSize: props.pageSize };
    const next = typeof updaterOrValue === "function" ? updaterOrValue(current) : updaterOrValue;
    emit("update:pagination", next);
  },
  getCoreRowModel: getCoreRowModel(),
  getFilteredRowModel: getFilteredRowModel(),
  getSortedRowModel: getSortedRowModel(),
});
</script>

<template>
  <div class="flex flex-1 scroll-mt-20 flex-col theme-container space-y-4">
    <DataTableToolbar
      :search="search"
      :status="status"
      :category="category"
      @update:search="emit('update:search', $event)"
      @update:status="emit('update:status', $event)"
      @update:category="emit('update:category', $event)"
    />
    <div class="rounded-md border">
      <Table>
        <TableHeader>
          <TableRow v-for="headerGroup in table.getHeaderGroups()" :key="headerGroup.id">
            <TableHead v-for="header in headerGroup.headers" :key="header.id">
              <FlexRender
                v-if="!header.isPlaceholder"
                :render="header.column.columnDef.header"
                :props="header.getContext()"
              />
            </TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          <template v-if="table.getRowModel().rows?.length">
            <TableRow
              v-for="row in table.getRowModel().rows"
              :key="row.id"
              :data-state="row.getIsSelected() && 'selected'"
              class="cursor-pointer hover:bg-muted/50 transition-colors"
              @click="router.push({ name: 'request-detail', params: { id: row.original.id } })"
            >
              <TableCell v-for="cell in row.getVisibleCells()" :key="cell.id">
                <FlexRender :render="cell.column.columnDef.cell" :props="cell.getContext()" />
              </TableCell>
            </TableRow>
          </template>

          <TableRow v-else>
            <TableCell :colspan="columns.length" class="h-24 text-center"> No results. </TableCell>
          </TableRow>
        </TableBody>
      </Table>
    </div>

    <DataTablePagination :table="table" />
  </div>
</template>
