<script setup>
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";

import NotificationBell from "@/components/NotificationBell.vue";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
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
const router = useRouter();

function logout() {
  auth.logout();
  router.push({ name: "login" });
}
</script>

<template>
  <nav
    class="mx-auto flex h-full w-full max-w-350 items-center border-dashed min-[1400px]:border-x min-[1800px]:max-w-384"
  >
    <div
      class="flex h-full w-full items-center justify-between gap-2 px-4 max-lg:gap-4 sm:px-6 lg:px-8"
    >
      <RouterLink :to="{ name: 'dashboard' }">Innovation Project Intake Portal</RouterLink>

      <div class="flex items-center gap-2">
        <NotificationBell />
        <DropdownMenu>
          <DropdownMenuTrigger as-child>
            <Button variant="ghost" class="relative h-8 w-8 rounded-full">
              <Avatar class="h-8 w-8">
                <AvatarFallback>{{ auth.name?.charAt(0)?.toUpperCase() || "U" }}</AvatarFallback>
              </Avatar>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent class="w-56" align="end">
            <DropdownMenuLabel class="font-normal">
              <div class="flex flex-col space-y-1">
                <p class="text-sm font-medium leading-none capitalize text-popover-foreground">
                  {{ auth.name }}
                </p>
                <p class="text-xs leading-none text-muted-foreground">{{ auth.email }}</p>
              </div>
            </DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem @click="logout"> Log out </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </div>
  </nav>
</template>
