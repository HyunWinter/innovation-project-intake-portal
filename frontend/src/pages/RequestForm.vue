<script setup>
import { reactive, ref, computed } from "vue";
import { useRouter } from "vue-router";

import { useApiStore } from "@/stores/api";

const api = useApiStore();
const router = useRouter();

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
  tech_category: "other", // Since this field has other, this should be required
  collaboration_interest: false,
  // Section 3: Scope
  title: "",
  description: "",
  objectives: "",
  outcomes: "",
  start_date: "",
  end_date: "",
  phases: "", // an array
  // Section 4: Resources
  funding_required: false,
  personnel: "",
  equipment: "",
  budget: "",
  estimated_roi: "",
});

const techCategories = [
  { value: "ai_ml", label: "AI / ML" },
  { value: "automation", label: "Automation" },
  { value: "business_process", label: "Business process" },
  { value: "other", label: "Other" },
];

const errors = ref({});
const submitting = ref(false);

// Inline checks (the same as server / for guardrail)
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
  if (!data.budget) delete data.budget; // let the server default it
  return data;
}

async function submit() {
  errors.value = {};
  if (clientError.value) return;
  submitting.value = true;
  try {
    const created = await api.createRequest(payload());
    router.push({ name: "request-detail", params: { id: created.id } });
  } catch (e) {
    errors.value = e.data && typeof e.data === "object" ? e.data : { detail: e.message };
  } finally {
    submitting.value = false;
  }
}
</script>

<template>
  <form class="flex flex-col gap-6" @submit.prevent="submit">
    <fieldset class="flex flex-col gap-2">
      <legend>1. Prior-Art Search</legend>
      <label class="flex flex-col">
        Keywords
        <input v-model="form.keywords" />
      </label>
      <label class="flex flex-col">
        Similar projects found
        <textarea v-model="form.similar_projects_found"></textarea>
      </label>
      <label class="flex flex-col">
        Differentiation
        <textarea v-model="form.differentiation"></textarea>
      </label>
      <label class="flex flex-col">
        Collaboration opportunities
        <textarea v-model="form.collaboration_opportunities"></textarea>
      </label>
    </fieldset>

    <fieldset class="flex flex-col gap-2">
      <legend>2. Basic Info</legend>
      <label class="flex flex-col">
        Contact name
        <input v-model="form.contact_name" required />
      </label>
      <label class="flex flex-col">
        Contact email
        <input v-model="form.contact_email" type="email" required />
      </label>
      <label class="flex flex-col">
        Site or team
        <input v-model="form.site_or_team" />
      </label>
      <label class="flex flex-col">
        Tech category
        <select v-model="form.tech_category" required>
          <option v-for="t in techCategories" :key="t.value" :value="t.value">
            {{ t.label }}
          </option>
        </select>
      </label>
      <label class="flex items-center gap-2">
        <input v-model="form.collaboration_interest" type="checkbox" />
        Open to collaboration
      </label>
    </fieldset>

    <fieldset class="flex flex-col gap-2">
      <legend>3. Scope</legend>
      <label class="flex flex-col">
        Title
        <input v-model="form.title" required />
      </label>
      <label class="flex flex-col">
        Description
        <textarea v-model="form.description" required></textarea>
      </label>
      <label class="flex flex-col">
        Objectives
        <textarea v-model="form.objectives" required></textarea>
      </label>
      <label class="flex flex-col">
        Outcomes
        <textarea v-model="form.outcomes"></textarea>
      </label>
      <label class="flex flex-col">
        Start date
        <input v-model="form.start_date" type="date" />
      </label>
      <label class="flex flex-col">
        End date
        <input v-model="form.end_date" type="date" />
      </label>
      <label class="flex flex-col">
        Phases (one per line)
        <textarea v-model="form.phases"></textarea>
      </label>
    </fieldset>

    <fieldset class="flex flex-col gap-2">
      <legend>4. Resources</legend>
      <label class="flex items-center gap-2">
        <input v-model="form.funding_required" type="checkbox" />
        Funding required
      </label>
      <label class="flex flex-col">
        Personnel
        <textarea v-model="form.personnel"></textarea>
      </label>
      <label class="flex flex-col">
        Equipment
        <textarea v-model="form.equipment"></textarea>
      </label>
      <template v-if="form.funding_required">
        <label class="flex flex-col">
          Budget
          <input v-model="form.budget" type="number" min="0" step="0.01" />
        </label>
        <label class="flex flex-col">
          Estimated ROI
          <textarea v-model="form.estimated_roi"></textarea>
        </label>
      </template>
    </fieldset>

    <p v-if="clientError">{{ clientError }}</p>
    <ul v-if="Object.keys(errors).length">
      <li v-for="(msg, field) in errors" :key="field">{{ field }}: {{ msg }}</li>
    </ul>

    <button type="submit" :disabled="submitting || !!clientError">
      {{ submitting ? "Submitting..." : "Submit" }}
    </button>
  </form>
</template>
