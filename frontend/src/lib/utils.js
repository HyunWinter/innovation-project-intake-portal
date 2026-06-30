import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

// Merge Tailwind classes, resolving conflicts.
export function cn(...inputs) {
  return twMerge(clsx(inputs));
}

// Apply a TanStack table updater (value or callback) to a Vue ref.
export function valueUpdater(updaterOrValue, ref) {
  ref.value = typeof updaterOrValue === "function" ? updaterOrValue(ref.value) : updaterOrValue;
}
