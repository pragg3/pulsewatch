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
  <div class="app">
    <header class="header">
      <div>
        <h1>PulseWatch</h1>
        <p>Simple uptime monitoring for your services.</p>
      </div>

      <span class="system-status">
        <span class="status-dot" />
        System Online
      </span>
    </header>

    <main class="dashboard">
      <section class="card">
        <div class="card-header">
          <div>
            <h2>Add Monitor</h2>
            <p>Start monitoring a new website or service.</p>
          </div>
        </div>

        <form
          class="monitor-form"
          @submit.prevent="addMonitor"
        >
          <div class="field">
            <label for="name">Name</label>
            <input
              id="name"
              v-model="name"
              type="text"
              placeholder="GitHub"
              required
            >
          </div>

          <div class="field">
            <label for="url">URL</label>
            <input
              id="url"
              v-model="url"
              type="url"
              placeholder="https://github.com"
              required
            >
          </div>

          <button
            type="submit"
            :disabled="submitting"
          >
            {{ submitting ? 'Adding...' : 'Add Monitor' }}
          </button>

          <p
            v-if="formError"
            class="error"
          >
            {{ formError }}
          </p>
        </form>
      </section>

      <section class="card">
        <div class="card-header monitor-heading">
          <div>
            <h2>Monitors</h2>
            <p>Your monitored services.</p>
          </div>

          <span class="count">
            {{ monitors.length }}
          </span>
        </div>

        <p
          v-if="loading"
          class="message"
        >
          Loading monitors...
        </p>

        <p
          v-else-if="error"
          class="error"
        >
          {{ error }}
        </p>

        <div
          v-else-if="monitors.length === 0"
          class="empty-state"
        >
          <div class="empty-icon">
            ◉
          </div>
          <h3>No monitors yet</h3>
          <p>Add your first monitor above.</p>
        </div>

        <div
          v-else
          class="monitor-list"
        >
          <article
            v-for="monitor in monitors"
            :key="monitor.id"
            class="monitor"
          >
            <div class="monitor-info">
              <span class="monitor-dot" />

              <div>
                <h3>{{ monitor.name }}</h3>

                <a
                  :href="monitor.url"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  {{ monitor.url }}
                </a>
              </div>
            </div>

            <span
              class="badge"
              :class="{ inactive: !monitor.is_active }"
            >
              {{ monitor.is_active ? 'Active' : 'Inactive' }}
            </span>
          </article>
        </div>
      </section>
    </main>

    <footer>
      PulseWatch · FastAPI · Vue · PostgreSQL · Docker
    </footer>
  </div>
</template>