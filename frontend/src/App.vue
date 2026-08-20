<script setup>
import { onMounted, ref } from 'vue'

const API_URL = import.meta.env.VITE_API_URL
const monitors = ref([])
const loading = ref(true)
const error = ref('')
const name = ref('')
const url = ref('')
const submitting = ref(false)
const formError = ref('')

async function loadMonitors() {
  try {
    const response = await fetch(`${API_URL}/monitors`)

    if (!response.ok) {
      throw new Error('Failed to load monitors')
    }

    monitors.value = await response.json()
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

async function addMonitor() {
  formError.value = ''
  submitting.value = true

  try {
    const response = await fetch(`${API_URL}/monitors`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        name: name.value,
        url: url.value,
      }),
    })

    if (!response.ok) {
      const data = await response.json()

      if (response.status === 409) {
        throw new Error(data.detail)
      }

      throw new Error('Failed to create monitor')
    }

    const newMonitor = await response.json()

    monitors.value.push(newMonitor)

    name.value = ''
    url.value = ''
  } catch (err) {
    formError.value = err.message
  } finally {
    submitting.value = false
  }
}

onMounted(loadMonitors)
</script>

<template>
  <main>
    <h1>PulseWatch</h1>
    <p>Website Monitoring Dashboard</p>
    <section>
      <h2>Add Monitor</h2>

      <form @submit.prevent="addMonitor">
        <div>
          <label for="name">Name</label>
          <input
            id="name"
            v-model="name"
            type="text"
            placeholder="GitLab"
            required
          >
        </div>

        <div>
          <label for="url">URL</label>
          <input
            id="url"
            v-model="url"
            type="url"
            placeholder="https://gitlab.com"
            required
          >
        </div>

        <button
          type="submit"
          :disabled="submitting"
        >
          {{ submitting ? 'Adding...' : 'Add Monitor' }}
        </button>

        <p v-if="formError">
          {{ formError }}
        </p>
      </form>
    </section>
    <section>
      <h2>Monitors</h2>

      <p v-if="loading">
        Loading monitors...
      </p>

      <p v-else-if="error">
        {{ error }}
      </p>

      <p v-else-if="monitors.length === 0">
        No monitors yet.
      </p>

      <ul v-else>
        <li
          v-for="monitor in monitors"
          :key="monitor.id"
        >
          <strong>{{ monitor.name }}</strong>
          —
          {{ monitor.url }}
        </li>
      </ul>
    </section>
  </main>
</template>