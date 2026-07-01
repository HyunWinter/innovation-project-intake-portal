<script setup>
import { ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Field, FieldDescription, FieldGroup, FieldLabel } from "@/components/ui/field";
import { Input } from "@/components/ui/input";

const auth = useAuthStore();
const router = useRouter();
const route = useRoute();

const email = ref("");
const password = ref("");
const error = ref("");
const loading = ref(false);

async function submit() {
  error.value = "";
  loading.value = true;
  try {
    await auth.login(email.value, password.value);
    router.push(route.query.next || { name: "dashboard" });
  } catch (e) {
    error.value = e.message || "Login failed";
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="flex flex-col gap-6">
    <Card class="overflow-hidden p-0">
      <CardContent class="grid p-0 md:grid-cols-2">
        <form class="px-6 md:px-8 py-20 md:py-24" @submit.prevent="submit">
          <FieldGroup>
            <div class="flex flex-col items-center gap-2 text-center">
              <h1 class="text-2xl font-bold">Innovation Project Intake Portal</h1>
              <p class="text-muted-foreground text-balance">Login to your company account</p>
            </div>
            <p v-if="error" class="text-sm text-destructive text-center">
              {{ error }}
            </p>
            <Field>
              <FieldLabel for="email"> Email </FieldLabel>
              <Input
                id="email"
                v-model="email"
                type="email"
                placeholder="email@address.com"
                required
              />
            </Field>
            <Field>
              <FieldLabel for="password"> Password </FieldLabel>
              <Input id="password" v-model="password" type="password" required />
            </Field>
            <Field>
              <Button type="submit" :disabled="loading">
                {{ loading ? "Logging in..." : "Login" }}
              </Button>
            </Field>
            <FieldDescription class="flex flex-col text-center">
              Forgot your account?
              <a
                href="https://github.com/HyunWinter/innovation-project-intake-portal#demo-credentials"
              >
                Check out the demo credentials.
              </a>
            </FieldDescription>
          </FieldGroup>
        </form>
        <div class="bg-muted relative hidden md:block">
          <img
            src="/login.jpg"
            alt="Image"
            draggable="false"
            class="absolute inset-0 h-full w-full object-cover dark:brightness-[0.2] dark:grayscale"
          />
        </div>
      </CardContent>
    </Card>
    <FieldDescription class="px-6 text-center">
      By clicking continue, you agree to our
      <a href="https://github.com/HyunWinter/innovation-project-intake-portal">Terms of Service</a>
      and
      <a href="https://github.com/HyunWinter/innovation-project-intake-portal">Privacy Policy</a>.
    </FieldDescription>
  </div>
</template>
