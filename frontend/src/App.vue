<script setup>
import { useCounterStore } from '@/stores/counter'
const counter = useCounterStore();
counter.startTimer()
</script>

<template>
  <h1 class="text-3xl font-bold underline">
    Hello World {{ counter.count }} Times!
  </h1>
</template>
