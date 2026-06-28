import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useCounterStore = defineStore('counter', () => {
  const count = ref(0)

  function increment() {
    count.value++
  }

  function startTimer() {
    if (this.intervalId) clearInterval(this.intervalId)

    this.intervalId = setInterval(() => {
      this.increment()
    }, 1000)
  }

  function stopTimer() {
    if (this.intervalId) {
      clearInterval(this.intervalId)
      this.intervalId = null
    }
  }

  return { count, increment, startTimer, stopTimer }
})