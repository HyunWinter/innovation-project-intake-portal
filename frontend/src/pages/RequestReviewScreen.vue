<script setup>
import { ref, reactive, computed, onMounted } from "vue";

import { useApiStore } from "@/stores/api";

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
onMounted(load);

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
  }));
  return [...comments, ...events].sort((a, b) => new Date(a.at) - new Date(b.at));
});

function label(action) {
  return action.replaceAll("_", " ");
}

function fieldType(field) {
  if (field === "presentation_date") return "datetime-local";
  if (field.endsWith("_date")) return "date";
  return "text";
}

// No required fields -> run straight away
// Required fields -> open the modal
function startAction(action) {
  actionError.value = "";
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
  <p v-if="loadError">{{ loadError }}</p>

  <div v-else-if="request">
    <header>
      <span>{{ request.category_label }}</span>
      <h1>{{ request.title }}</h1>
      <span>{{ request.status_label }}</span>
    </header>

    <ol>
      <li v-for="step in request.workflow" :key="step.status">
        {{ step.label }} ({{ step.state }})
      </li>
    </ol>

    <div>
      <button
        v-for="a in request.available_actions"
        :key="a.action"
        type="button"
        @click="startAction(a)"
      >
        {{ label(a.action) }}
      </button>
      <p v-if="actionError">{{ actionError }}</p>
    </div>

    <div v-if="acting">
      <h2>{{ label(acting.action) }}</h2>
      <label v-for="f in acting.required_fields" :key="f">
        {{ f }}
        <input v-model="fieldValues[f]" :type="fieldType(f)" />
      </label>
      <button type="button" @click="submitModal">Confirm</button>
      <button type="button" @click="acting = null">Cancel</button>
    </div>

    <section>
      <h2>Timeline</h2>
      <ul>
        <li v-for="(item, i) in timeline" :key="i">
          <template v-if="item.kind === 'comment'">
            {{ item.who }} commented: {{ item.body }} <small>{{ item.at }}</small>
          </template>
          <template v-else>
            {{ item.who }} {{ label(item.type) }}
            <span v-if="item.from || item.to">({{ item.from }} &rarr; {{ item.to }})</span>
            <small>{{ item.at }}</small>
          </template>
        </li>
      </ul>
    </section>
  </div>
</template>
