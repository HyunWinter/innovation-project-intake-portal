<script setup>
import { reactive, ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";

import { useApiStore } from "@/stores/api";
import { TECH_CATEGORIES } from "@/lib/constants";
import Container from "@/components/Container.vue";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";

const api = useApiStore();
const router = useRouter();

const savingDraft = ref(false);
const draftSavedMessage = ref("");

onMounted(async () => {
  try {
    const draft = await api.getDraft();
    if (draft && draft.data) {
      Object.assign(form, draft.data);
    }
  } catch (e) {
    if (e.status !== 404) console.error("Failed to load draft", e);
  }
});

const currentStep = ref(1);
const steps = [
  { id: 1, name: "Prior-Art" },
  { id: 2, name: "Basic Info" },
  { id: 3, name: "Scope" },
  { id: 4, name: "Resources" },
];

const stepRequirements = {
  2: ["contact_name", "contact_email", "tech_category"],
  3: ["title", "description", "objectives"],
};

function validateStep(step) {
  errors.value = {};
  let valid = true;

  const requiredFields = stepRequirements[step] || [];
  for (const field of requiredFields) {
    const val = form[field];
    if (!val || (typeof val === "string" && !val.trim())) {
      errors.value[field] = "This field is required.";
      valid = false;
    }
  }

  if (step === 3 && form.start_date && form.end_date && form.end_date < form.start_date) {
    errors.value.end_date = "End date must be on or after the start date.";
    valid = false;
  }

  return valid;
}

function nextStep() {
  if (validateStep(currentStep.value)) {
    if (currentStep.value < 4) currentStep.value++;
    errors.value = {}; // clear errors when moving to next step
  }
}

function prevStep() {
  if (currentStep.value > 1) currentStep.value--;
}

const form = reactive({
  // Section 1: Prior-Art
  keywords: "",
  similar_projects_found: "",
  differentiation: "",
  collaboration_opportunities: "",
  // Section 2: Basic info
  contact_name: "",
  contact_email: "",
  site_or_team: "",
  tech_category: "other",
  collaboration_interest: false,
  // Section 3: Scope
  title: "",
  description: "",
  objectives: "",
  outcomes: "",
  start_date: "",
  end_date: "",
  phases: "",
  // Section 4: Resources
  funding_required: false,
  personnel: "",
  equipment: "",
  budget: "",
  estimated_roi: "",
});

const errors = ref({});
const submitting = ref(false);

const clientError = computed(() => {
  if (form.start_date && form.end_date && form.end_date < form.start_date) {
    return "End date must be on or after the start date.";
  }
  if (form.funding_required) {
    if (!form.budget || Number(form.budget) <= 0) {
      return "Funded proposals need a budget greater than 0.";
    }
    if (!form.estimated_roi) {
      return "Funded proposals need an estimated ROI.";
    }
  }
  return "";
});

function payload() {
  const data = { ...form };
  data.phases = form.phases
    ? form.phases
        .split("\n")
        .map((p) => p.trim())
        .filter(Boolean)
    : [];
  if (!data.budget) delete data.budget;
  if (!data.start_date) delete data.start_date;
  if (!data.end_date) delete data.end_date;
  return data;
}

async function saveDraftAction() {
  savingDraft.value = true;
  draftSavedMessage.value = "";
  try {
    await api.saveDraft({ data: form });
    draftSavedMessage.value = "Draft saved successfully.";
    setTimeout(() => (draftSavedMessage.value = ""), 3000);
  } catch (e) {
    errors.value = { detail: "Failed to save draft." };
  } finally {
    savingDraft.value = false;
  }
}

async function submit() {
  errors.value = {};
  if (clientError.value) return;
  submitting.value = true;
  try {
    const created = await api.createRequest(payload());
    await api.deleteDraft().catch(() => null);
    router.push({ name: "request-detail", params: { id: created.id } });
  } catch (e) {
    errors.value = e.data && typeof e.data === "object" ? e.data : { detail: e.message };
  } finally {
    submitting.value = false;
  }
}
</script>

<template>
  <Container>
    <div class="mb-8">
      <h2 class="text-2xl font-bold tracking-tight">New Innovation Request</h2>
      <p class="text-muted-foreground">Please provide the details for your new project proposal.</p>
    </div>

    <!-- Stepper -->
    <div class="mb-12 flex items-center justify-between w-full max-w-3xl mx-auto px-4">
      <template v-for="(step, index) in steps" :key="step.id">
        <!-- Circle -->
        <div class="relative flex flex-col items-center justify-center shrink-0">
          <div
            class="w-10 h-10 rounded-full border-2 flex items-center justify-center bg-background z-10"
            :class="[
              currentStep > step.id
                ? 'border-primary bg-primary text-primary-foreground'
                : currentStep === step.id
                  ? 'border-primary text-primary'
                  : 'border-muted text-muted-foreground',
            ]"
          >
            <svg
              v-if="currentStep > step.id"
              xmlns="http://www.w3.org/2000/svg"
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="3"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <polyline points="20 6 9 17 4 12"></polyline>
            </svg>
            <span v-else class="text-sm font-bold">{{ step.id }}</span>
          </div>
          <span
            class="absolute top-12 text-xs font-semibold whitespace-nowrap"
            :class="currentStep >= step.id ? 'text-foreground' : 'text-muted-foreground'"
          >
            {{ step.name }}
          </span>
        </div>
        <!-- Line -->
        <div
          v-if="index !== steps.length - 1"
          class="flex-1 h-0.5 mx-2 sm:mx-4"
          :class="currentStep > step.id ? 'bg-primary' : 'bg-muted'"
        ></div>
      </template>
    </div>

    <form class="flex flex-col gap-8 pb-16" @submit.prevent="submit">
      <!-- Section 1: Prior-Art -->
      <Card v-show="currentStep === 1">
        <CardHeader>
          <CardTitle>1. Prior-Art Search</CardTitle>
          <CardDescription>Information about existing or similar projects.</CardDescription>
        </CardHeader>
        <CardContent class="grid gap-6">
          <div class="grid gap-2">
            <Label for="keywords">Keywords</Label>
            <Input
              id="keywords"
              v-model="form.keywords"
              placeholder="e.g. AI, Machine Learning, Automation"
            />
          </div>
          <div class="grid gap-2">
            <Label for="similar_projects_found">Similar projects found</Label>
            <textarea
              id="similar_projects_found"
              v-model="form.similar_projects_found"
              class="flex min-h-[80px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
            ></textarea>
          </div>
          <div class="grid gap-2">
            <Label for="differentiation">Differentiation</Label>
            <textarea
              id="differentiation"
              v-model="form.differentiation"
              class="flex min-h-[80px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
            ></textarea>
          </div>
          <div class="grid gap-2">
            <Label for="collaboration_opportunities">Collaboration opportunities</Label>
            <textarea
              id="collaboration_opportunities"
              v-model="form.collaboration_opportunities"
              class="flex min-h-[80px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
            ></textarea>
          </div>
        </CardContent>
      </Card>

      <!-- Section 2: Basic Info -->
      <Card v-show="currentStep === 2">
        <CardHeader>
          <CardTitle>2. Basic Info</CardTitle>
          <CardDescription>Contact information and categorization.</CardDescription>
        </CardHeader>
        <CardContent class="grid gap-6 sm:grid-cols-2">
          <div class="grid gap-2">
            <Label for="contact_name">Contact name <span class="text-destructive">*</span></Label>
            <Input id="contact_name" v-model="form.contact_name" />
          </div>
          <div class="grid gap-2">
            <Label for="contact_email">Contact email <span class="text-destructive">*</span></Label>
            <Input id="contact_email" type="email" v-model="form.contact_email" />
          </div>
          <div class="grid gap-2">
            <Label for="site_or_team">Site or team</Label>
            <Input id="site_or_team" v-model="form.site_or_team" />
          </div>
          <div class="grid gap-2">
            <Label for="tech_category">Tech category <span class="text-destructive">*</span></Label>
            <select
              id="tech_category"
              v-model="form.tech_category"
              class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
            >
              <option v-for="t in TECH_CATEGORIES" :key="t.value" :value="t.value">
                {{ t.label }}
              </option>
            </select>
          </div>
          <div class="grid gap-2 sm:col-span-2 mt-2">
            <Label class="flex items-center gap-2 cursor-pointer">
              <input
                v-model="form.collaboration_interest"
                type="checkbox"
                class="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
              />
              Open to collaboration
            </Label>
          </div>
        </CardContent>
      </Card>

      <!-- Section 3: Scope -->
      <Card v-show="currentStep === 3">
        <CardHeader>
          <CardTitle>3. Scope</CardTitle>
          <CardDescription
            >Details about the project's goals, timeline, and phases.</CardDescription
          >
        </CardHeader>
        <CardContent class="grid gap-6">
          <div class="grid gap-2">
            <Label for="title">Title <span class="text-destructive">*</span></Label>
            <Input id="title" v-model="form.title" />
          </div>
          <div class="grid gap-2">
            <Label for="description">Description <span class="text-destructive">*</span></Label>
            <textarea
              id="description"
              v-model="form.description"
              class="flex min-h-[80px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
            ></textarea>
          </div>
          <div class="grid gap-2">
            <Label for="objectives">Objectives <span class="text-destructive">*</span></Label>
            <textarea
              id="objectives"
              v-model="form.objectives"
              class="flex min-h-[80px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
            ></textarea>
          </div>
          <div class="grid gap-2">
            <Label for="outcomes">Outcomes</Label>
            <textarea
              id="outcomes"
              v-model="form.outcomes"
              class="flex min-h-[80px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
            ></textarea>
          </div>
          <div class="grid sm:grid-cols-2 gap-6">
            <div class="grid gap-2">
              <Label for="start_date">Start date</Label>
              <Input id="start_date" v-model="form.start_date" type="date" />
            </div>
            <div class="grid gap-2">
              <Label for="end_date">End date</Label>
              <Input id="end_date" v-model="form.end_date" type="date" />
            </div>
          </div>
          <div class="grid gap-2">
            <Label for="phases">Phases (one per line)</Label>
            <textarea
              id="phases"
              v-model="form.phases"
              class="flex min-h-[80px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
            ></textarea>
          </div>
        </CardContent>
      </Card>

      <!-- Section 4: Resources -->
      <Card v-show="currentStep === 4">
        <CardHeader>
          <CardTitle>4. Resources</CardTitle>
          <CardDescription>Personnel, equipment, and funding needs.</CardDescription>
        </CardHeader>
        <CardContent class="grid gap-6">
          <div class="grid gap-2">
            <Label for="personnel">Personnel</Label>
            <textarea
              id="personnel"
              v-model="form.personnel"
              class="flex min-h-[80px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
            ></textarea>
          </div>
          <div class="grid gap-2">
            <Label for="equipment">Equipment</Label>
            <textarea
              id="equipment"
              v-model="form.equipment"
              class="flex min-h-[80px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
            ></textarea>
          </div>

          <div class="grid gap-2 mt-4 pt-4 border-t">
            <Label class="flex items-center gap-2 cursor-pointer">
              <input
                v-model="form.funding_required"
                type="checkbox"
                class="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
              />
              Funding required
            </Label>
          </div>

          <!-- Budget & ROI only show when funding is required -->
          <div v-if="form.funding_required" class="grid sm:grid-cols-2 gap-6 items-start">
            <div class="grid gap-2">
              <Label for="budget">Budget ($) <span class="text-destructive">*</span></Label>
              <Input
                id="budget"
                v-model="form.budget"
                type="number"
                min="0"
                step="0.01"
                placeholder="0.00"
              />
            </div>
            <div class="grid gap-2">
              <Label for="estimated_roi"
                >Estimated ROI <span class="text-destructive">*</span></Label
              >
              <textarea
                id="estimated_roi"
                v-model="form.estimated_roi"
                placeholder="Describe the expected return on investment..."
                class="flex min-h-[80px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
              ></textarea>
            </div>
          </div>
        </CardContent>
      </Card>

      <!-- Validation & Submit -->
      <div class="flex flex-col gap-4">
        <div
          v-if="clientError && currentStep === 4"
          class="rounded-md bg-destructive/15 p-3 text-sm text-destructive font-medium border border-destructive/20"
        >
          {{ clientError }}
        </div>

        <div
          v-if="Object.keys(errors).length"
          class="rounded-md bg-destructive/15 p-3 text-sm text-destructive font-medium border border-destructive/20"
        >
          <ul class="list-disc pl-5">
            <li v-for="(msg, field) in errors" :key="field">
              <span class="capitalize">{{ field.replace("_", " ") }}</span
              >: {{ Array.isArray(msg) ? msg[0] : msg }}
            </li>
          </ul>
        </div>

        <div v-if="draftSavedMessage" class="text-sm font-medium text-primary">
          {{ draftSavedMessage }}
        </div>

        <div class="flex justify-between gap-4">
          <Button
            type="button"
            variant="outline"
            @click="currentStep > 1 ? prevStep() : router.back()"
          >
            {{ currentStep > 1 ? "Previous" : "Cancel" }}
          </Button>

          <div class="flex gap-2">
            <Button
              type="button"
              variant="secondary"
              @click="saveDraftAction"
              :disabled="savingDraft"
            >
              {{ savingDraft ? "Saving..." : "Save Draft" }}
            </Button>
            <Button v-if="currentStep < 4" type="button" @click="nextStep()"> Next Step </Button>
            <Button v-else type="submit" :disabled="submitting || !!clientError">
              {{ submitting ? "Submitting..." : "Submit Proposal" }}
            </Button>
          </div>
        </div>
      </div>
    </form>
  </Container>
</template>
