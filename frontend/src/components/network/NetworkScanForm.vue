<script setup>
import { ref } from 'vue'

import '../../assets/styles/network-scan-form.css'

defineProps({
  disabled: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['discover'])

const startIp = ref('')
const endIp = ref('')

function submit() {
  emit('discover', {
    startIp: startIp.value.trim(),
    endIp: endIp.value.trim(),
  })
}
</script>

<template>
  <form
    class="network-scan-form"
    @submit.prevent="submit"
  >
    <div class="network-range">
      <div class="field">
        <label for="network-start-ip">
          Starting IP
        </label>

        <input
          id="network-start-ip"
          v-model="startIp"
          type="text"
          inputmode="decimal"
          autocomplete="off"
          placeholder="Enter starting IP"
          required
        >
      </div>

      <div class="field">
        <label for="network-end-ip">
          Ending IP
        </label>

        <input
          id="network-end-ip"
          v-model="endIp"
          type="text"
          inputmode="decimal"
          autocomplete="off"
          placeholder="Enter ending IP"
          required
        >
      </div>
    </div>

    <p class="network-scan-hint">
      Enter the internal IP range you are authorized
      to inspect.
    </p>

    <button
      type="submit"
      :disabled="disabled"
    >
      {{ disabled ? 'Discovering...' : 'Discover' }}
    </button>
  </form>
</template>