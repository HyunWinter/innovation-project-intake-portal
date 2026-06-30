import { h } from "vue";
import { TECH_CATEGORY_LABELS } from "@/lib/constants";
import { Badge } from "@/components/ui/badge";

// Column definitions for the request dashboard table.
// Keys match RequestListSerializer fields.
export const columns = [
  {
    accessorKey: "title",
    header: "Title",
    cell: ({ row }) => {
      const techVal = row.original.tech_category;
      const techLabel = TECH_CATEGORY_LABELS[techVal] || "Other";
      return h("div", { class: "flex items-center gap-2" }, [
        h(Badge, { variant: "secondary" }, () => techLabel),
        h("span", { class: "font-medium" }, row.getValue("title")),
      ]);
    },
  },
  {
    accessorKey: "status_label",
    header: "Status",
    cell: ({ row }) => {
      const s = row.original.status;
      const label = row.getValue("status_label");
      let variant = "secondary";
      if (s === "approved") {
        variant = "default";
      } else if (s === "rejected") {
        variant = "outline";
      }
      return h(Badge, { variant }, () => label);
    },
  },
  {
    accessorKey: "category_label",
    header: "Category",
    cell: ({ row }) => row.getValue("category_label"),
  },
  {
    accessorKey: "submitter_name",
    header: "Submitter",
    cell: ({ row }) => row.getValue("submitter_name"),
  },
  {
    accessorKey: "updated_at",
    header: "Updated",
    cell: ({ row }) => {
      const value = row.getValue("updated_at");
      return value ? new Date(value).toLocaleDateString() : "";
    },
  },
  {
    accessorKey: "is_overdue",
    header: "Overdue",
    cell: ({ row }) => {
      return row.getValue("is_overdue")
        ? h(Badge, { variant: "destructive" }, () => "Overdue")
        : "";
    },
  },
];
