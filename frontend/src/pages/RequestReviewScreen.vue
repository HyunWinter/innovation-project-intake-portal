<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, watch } from "vue";
import { useApiStore } from "@/stores/api";
import { TECH_CATEGORY_LABELS } from "@/lib/constants";
import Container from "@/components/Container.vue";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
} from "@/components/ui/card";

const props = defineProps({ id: { type: String, required: true } });
const api = useApiStore();

const request = ref(null);
const loadError = ref("");
const actionError = ref("");

// The action from the modal
// null = closed
const acting = ref(null);
const fieldValues = reactive({});

// Lifecycle
async function load() {
  loadError.value = "";
  try {
    request.value = await api.getRequest(props.id);
  } catch (e) {
    loadError.value = e.message;
  }
}
onMounted(() => {
  load();
  window.addEventListener("refresh-request-data", load);
});

onUnmounted(() => {
  window.removeEventListener("refresh-request-data", load);
});

watch(() => props.id, load);

// Comments and events
const timeline = computed(() => {
  if (!request.value) return [];
  const comments = (request.value.comments || []).map((c) => ({
    kind: "comment",
    at: c.created_at,
    who: c.author_name,
    body: c.body,
  }));
  const events = (request.value.audit_events || []).map((e) => ({
    kind: "event",
    at: e.created_at,
    who: e.actor_name,
    type: e.event_type,
    from: e.from_status,
    to: e.to_status,
    payload: e.payload,
  }));
  return [...comments, ...events].sort((a, b) => new Date(a.at) - new Date(b.at));
});

function label(action) {
  const customLabels = {
    go: "Approve Funding",
    no_go: "Reject Funding",
    start: "Begin Execution",
    advanced: "Presentation Successful",
    not_advanced: "Presentation Failed",
    combine_existing: "Combine with Existing Project",
    enhance_search: "Enhance Prior-Art Search",
  };
  if (customLabels[action]) return customLabels[action];

  return action.replaceAll("_", " ");
}

function fieldType(field) {
  if (field === "presentation_date") return "datetime-local";
  if (field.endsWith("_date")) return "date";
  return "text";
}

function hasVisiblePayload(payload) {
  if (!payload) return false;
  const ignored = ["committee_decision", "presentation_status", "funding_status"];
  return Object.entries(payload).some(([k, v]) => v && !ignored.includes(k));
}

// No required fields -> run straight away
// Required fields -> open the modal
function startAction(action) {
  actionError.value = "";

  // Clear previous field values to prevent stale data submission
  for (const k of Object.keys(fieldValues)) delete fieldValues[k];

  if (!action.required_fields.length) {
    runAction(action, {});
    return;
  }

  for (const field of action.required_fields) fieldValues[field] = "";
  acting.value = action;
}

async function runAction(action, payload) {
  actionError.value = "";
  try {
    // The transition response -> the updated request
    request.value = await api.runTransition(props.id, action.endpoint, {
      action: action.action,
      ...payload,
    });
    acting.value = null;
  } catch (e) {
    actionError.value = e.message;
  }
}

function submitModal() {
  runAction(acting.value, { ...fieldValues });
}
</script>

<template>
  <Container>
    <div
      v-if="loadError"
      class="rounded-md bg-destructive/15 p-4 text-destructive border border-destructive/20 font-medium"
    >
      {{ loadError }}
    </div>

    <div v-else-if="request" class="space-y-8 pb-16">
      <!-- Status Header & Category Badge -->
      <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <div class="flex items-center gap-2 mb-2">
            <Badge variant="secondary">
              {{ TECH_CATEGORY_LABELS[request.tech_category] || request.tech_category || "N/A" }}
            </Badge>
            <Badge variant="secondary">
              {{ request.category_label }}
            </Badge>
            <Badge
              :variant="
                request.status === 'approved'
                  ? 'default'
                  : request.status === 'rejected'
                    ? 'outline'
                    : 'secondary'
              "
            >
              {{ request.status_label }}
            </Badge>
          </div>
          <h1 class="text-3xl font-bold tracking-tight">{{ request.title }}</h1>
          <p class="text-muted-foreground mt-1">
            Submitted by
            <span class="font-medium text-foreground">{{ request.submitter_name }}</span> on
            {{ new Date(request.created_at).toLocaleDateString() }}
          </p>
        </div>
      </div>

      <div
        v-if="actionError"
        class="rounded-md bg-destructive/15 p-3 text-sm text-destructive font-medium border border-destructive/20"
      >
        {{ actionError }}
      </div>

      <!-- Workflow Progress Component -->
      <Card>
        <CardHeader class="pb-4">
          <CardTitle class="text-lg">Workflow Progress</CardTitle>
        </CardHeader>
        <CardContent>
          <div
            class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 relative"
          >
            <div class="hidden sm:block absolute top-4 left-4 right-4 h-0.5 bg-muted z-0"></div>

            <div
              v-for="(step, index) in request.workflow"
              :key="step.status"
              class="relative z-10 flex flex-row sm:flex-col items-center gap-3 sm:gap-2 bg-card px-2 flex-1 sm:flex-none"
            >
              <div
                class="w-8 h-8 rounded-full border-2 flex items-center justify-center bg-card transition-colors shrink-0"
                :class="[
                  step.state === 'complete'
                    ? 'border-primary bg-primary text-primary-foreground'
                    : step.state === 'current'
                      ? 'border-primary text-primary'
                      : 'border-muted text-muted-foreground',
                ]"
              >
                <svg
                  v-if="step.state === 'complete'"
                  xmlns="http://www.w3.org/2000/svg"
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="3"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <polyline points="20 6 9 17 4 12"></polyline>
                </svg>
                <span v-else class="text-xs font-bold">{{ index + 1 }}</span>
              </div>
              <span
                class="text-sm font-medium text-left sm:text-center sm:max-w-[100px]"
                :class="step.state === 'pending' ? 'text-muted-foreground' : 'text-foreground'"
              >
                {{ step.label }}
              </span>
            </div>
          </div>
        </CardContent>
      </Card>

      <!-- Main Layout -->
      <div class="grid lg:grid-cols-3 gap-6">
        <!-- Left Column: Details -->
        <div class="lg:col-span-2 space-y-6">
          <!-- Scope -->
          <Card>
            <CardHeader>
              <CardTitle>Scope</CardTitle>
            </CardHeader>
            <CardContent class="space-y-6">
              <div>
                <h4 class="text-sm font-semibold text-muted-foreground mb-1">Description</h4>
                <p class="text-sm whitespace-pre-wrap">{{ request.description || "N/A" }}</p>
              </div>
              <div class="grid sm:grid-cols-2 gap-6">
                <div>
                  <h4 class="text-sm font-semibold text-muted-foreground mb-1">Objectives</h4>
                  <p class="text-sm whitespace-pre-wrap">{{ request.objectives || "N/A" }}</p>
                </div>
                <div>
                  <h4 class="text-sm font-semibold text-muted-foreground mb-1">Outcomes</h4>
                  <p class="text-sm whitespace-pre-wrap">{{ request.outcomes || "N/A" }}</p>
                </div>
              </div>

              <div
                class="grid sm:grid-cols-2 gap-6 pt-4 border-t"
                v-if="
                  request.start_date ||
                  request.end_date ||
                  (request.phases && request.phases.length)
                "
              >
                <div class="flex gap-6" v-if="request.start_date || request.end_date">
                  <div v-if="request.start_date">
                    <h4 class="text-sm font-semibold text-muted-foreground mb-1">Start Date</h4>
                    <p class="text-sm">{{ request.start_date }}</p>
                  </div>
                  <div v-if="request.end_date">
                    <h4 class="text-sm font-semibold text-muted-foreground mb-1">End Date</h4>
                    <p class="text-sm">{{ request.end_date }}</p>
                  </div>
                </div>
                <div
                  v-if="request.phases && request.phases.length"
                  :class="request.start_date ? 'sm:col-span-1' : 'sm:col-span-2'"
                >
                  <h4 class="text-sm font-semibold text-muted-foreground mb-2">Phases</h4>
                  <ul class="list-disc pl-5 text-sm space-y-1 text-muted-foreground">
                    <li v-for="(phase, i) in request.phases" :key="i">{{ phase }}</li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>

          <!-- Context & Prior-Art -->
          <Card>
            <CardHeader>
              <CardTitle>Context & Prior-Art</CardTitle>
            </CardHeader>
            <CardContent class="space-y-6">
              <div class="grid sm:grid-cols-2 gap-6">
                <div>
                  <h4 class="text-sm font-semibold text-muted-foreground mb-1">Contact</h4>
                  <p class="text-sm">
                    {{ request.contact_name || "N/A" }}
                    <span v-if="request.contact_email" class="text-muted-foreground">
                      ({{ request.contact_email }})
                    </span>
                  </p>
                </div>
                <div>
                  <h4 class="text-sm font-semibold text-muted-foreground mb-1">Site / Team</h4>
                  <p class="text-sm">{{ request.site_or_team || "N/A" }}</p>
                </div>
                <div>
                  <h4 class="text-sm font-semibold text-muted-foreground mb-1">Tech Category</h4>
                  <p class="text-sm">
                    {{
                      TECH_CATEGORY_LABELS[request.tech_category] || request.tech_category || "N/A"
                    }}
                  </p>
                </div>
                <div>
                  <h4 class="text-sm font-semibold text-muted-foreground mb-1">Collaboration</h4>
                  <p class="text-sm">
                    {{ request.collaboration_interest ? "Open to collaboration" : "Not specified" }}
                  </p>
                </div>
              </div>

              <div class="space-y-6 pt-4 border-t">
                <div v-if="request.keywords">
                  <h4 class="text-sm font-semibold text-muted-foreground mb-1">Keywords</h4>
                  <p class="text-sm">{{ request.keywords }}</p>
                </div>
                <div class="grid sm:grid-cols-2 gap-6">
                  <div v-if="request.similar_projects_found">
                    <h4 class="text-sm font-semibold text-muted-foreground mb-1">
                      Similar Projects
                    </h4>
                    <p class="text-sm whitespace-pre-wrap">{{ request.similar_projects_found }}</p>
                  </div>
                  <div v-if="request.differentiation">
                    <h4 class="text-sm font-semibold text-muted-foreground mb-1">
                      Differentiation
                    </h4>
                    <p class="text-sm whitespace-pre-wrap">{{ request.differentiation }}</p>
                  </div>
                </div>
                <div v-if="request.collaboration_opportunities">
                  <h4 class="text-sm font-semibold text-muted-foreground mb-1">
                    Collaboration Opportunities
                  </h4>
                  <p class="text-sm whitespace-pre-wrap">
                    {{ request.collaboration_opportunities }}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <!-- Resources & Budget -->
          <Card>
            <CardHeader>
              <CardTitle>Resources & Budget</CardTitle>
            </CardHeader>
            <CardContent class="space-y-6">
              <div class="grid sm:grid-cols-2 gap-6">
                <div>
                  <h4 class="text-sm font-semibold text-muted-foreground mb-1">Personnel</h4>
                  <p class="text-sm whitespace-pre-wrap">
                    {{ request.personnel || "None specified" }}
                  </p>
                </div>
                <div>
                  <h4 class="text-sm font-semibold text-muted-foreground mb-1">Equipment</h4>
                  <p class="text-sm whitespace-pre-wrap">
                    {{ request.equipment || "None specified" }}
                  </p>
                </div>
              </div>

              <div class="pt-4 border-t" v-if="request.funding_required">
                <div class="grid sm:grid-cols-2 gap-6">
                  <div>
                    <h4 class="text-sm font-semibold text-muted-foreground mb-1">
                      Budget Required
                    </h4>
                    <p class="text-sm font-medium text-foreground">
                      ${{ Number(request.budget).toLocaleString() }}
                    </p>
                  </div>
                  <div>
                    <h4 class="text-sm font-semibold text-muted-foreground mb-1">Estimated ROI</h4>
                    <p class="text-sm whitespace-pre-wrap">{{ request.estimated_roi }}</p>
                  </div>
                </div>
              </div>
              <div class="pt-4 border-t" v-else>
                <p class="text-sm text-muted-foreground">No additional funding required.</p>
              </div>
            </CardContent>
          </Card>
        </div>

        <!-- Right Column: Timeline -->
        <div class="space-y-6">
          <Card class="h-full">
            <CardHeader>
              <CardTitle>Timeline & Activity</CardTitle>
            </CardHeader>
            <CardContent>
              <div class="space-y-6">
                <div
                  v-for="(item, i) in timeline"
                  :key="i"
                  class="relative pl-6 before:absolute before:left-2 before:top-2 before:h-full before:w-px before:bg-border last:before:hidden"
                >
                  <!-- Indicator -->
                  <div
                    class="absolute left-[3px] top-1.5 h-2.5 w-2.5 rounded-full border-2 border-card ring-2"
                    :class="
                      item.kind === 'comment'
                        ? 'bg-primary ring-primary/30'
                        : 'bg-muted-foreground ring-muted'
                    "
                  ></div>

                  <div class="text-sm">
                    <!-- Human Comment -->
                    <template v-if="item.kind === 'comment'">
                      <p class="font-medium text-foreground">{{ item.who }}</p>
                      <div
                        class="mt-1.5 bg-muted/50 p-3 rounded-md border border-border/50 text-foreground whitespace-pre-wrap"
                      >
                        {{ item.body }}
                      </div>
                    </template>

                    <!-- System Event -->
                    <template v-else>
                      <p class="text-muted-foreground flex items-center flex-wrap gap-1.5">
                        <span class="font-medium text-foreground">{{ item.who }}</span>
                        <span class="text-muted-foreground/50">&middot;</span>
                        <strong class="capitalize font-semibold text-foreground">{{
                          label(item.type)
                        }}</strong>
                        <span
                          v-if="item.from && item.to && item.from !== item.to"
                          class="inline-block ml-1 px-1.5 py-0.5 rounded-md bg-muted text-xs"
                        >
                          {{ label(item.from) }} &rarr; {{ label(item.to) }}
                        </span>
                      </p>
                      <div
                        v-if="hasVisiblePayload(item.payload)"
                        class="mt-2 bg-muted/30 p-3 rounded-md border border-border/50 text-sm text-foreground space-y-2"
                      >
                        <template v-for="(val, key) in item.payload" :key="key">
                          <div
                            v-if="
                              val &&
                              ![
                                'committee_decision',
                                'presentation_status',
                                'funding_status',
                              ].includes(key)
                            "
                          >
                            <span
                              class="font-semibold text-muted-foreground capitalize text-xs block mb-0.5"
                              >{{ label(key) }}</span
                            >
                            <span class="whitespace-pre-wrap">{{ val }}</span>
                          </div>
                        </template>
                      </div>
                    </template>
                    <p class="text-xs text-muted-foreground mt-1">
                      {{ new Date(item.at).toLocaleString() }}
                    </p>
                  </div>
                </div>

                <div
                  v-if="timeline.length === 0"
                  class="text-sm text-muted-foreground text-center py-4"
                >
                  No activity recorded yet.
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      <!-- Role+State Gated Actions -->
      <div
        class="flex flex-wrap justify-end gap-3 mt-8 pt-6 border-t"
        v-if="request.available_actions?.length"
      >
        <Button
          v-for="a in request.available_actions"
          :key="a.action"
          :variant="
            a.action.includes('reject') || a.action.includes('no_go') ? 'destructive' : 'outline'
          "
          @click="startAction(a)"
        >
          <span class="capitalize">{{ label(a.action) }}</span>
        </Button>
      </div>
    </div>

    <!-- Committee Decision Modal -->
    <div
      v-if="acting"
      class="fixed inset-0 z-50 bg-background/80 backdrop-blur-sm flex items-center justify-center p-4"
    >
      <Card class="w-full max-w-lg shadow-xl border-2 animate-in zoom-in-95 duration-200">
        <CardHeader>
          <CardTitle class="capitalize text-xl">{{ label(acting.action) }}</CardTitle>
          <CardDescription
            >Please provide the required details to complete this action.</CardDescription
          >
        </CardHeader>
        <CardContent class="grid gap-5">
          <div
            v-if="actionError"
            class="rounded-md bg-destructive/15 p-3 text-sm text-destructive font-medium border border-destructive/20"
          >
            {{ actionError }}
          </div>
          <div v-for="f in acting.required_fields" :key="f" class="grid gap-2">
            <Label :for="f" class="capitalize font-semibold text-foreground"
              >{{ f.replaceAll("_", " ") }} <span class="text-destructive">*</span></Label
            >

            <textarea
              v-if="fieldType(f) === 'text' && (f.includes('reasoning') || f === 'body')"
              :id="f"
              v-model="fieldValues[f]"
              class="flex min-h-[100px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
              placeholder="Enter details..."
            ></textarea>

            <Input v-else :id="f" v-model="fieldValues[f]" :type="fieldType(f)" />
          </div>
        </CardContent>
        <CardFooter class="flex justify-end gap-3 border-t bg-muted/20 pt-4">
          <Button
            variant="outline"
            @click="
              acting = null;
              actionError = '';
            "
            >Cancel</Button
          >
          <Button @click="submitModal">Confirm</Button>
        </CardFooter>
      </Card>
    </div>
  </Container>
</template>
