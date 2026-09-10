<script setup>
import { ref } from 'vue'

import '../../assets/styles/network-discovery.css'

import {
  discoverNetwork,
  getNetworkInfo,
} from '../../services/networkApi'

import NetworkInfo from './NetworkInfo.vue'
import NetworkResults from './NetworkResults.vue'
import NetworkScanForm from './NetworkScanForm.vue'

const discoveryKey = ref('')

const authenticated = ref(false)
const authenticating = ref(false)
const authError = ref('')

const networkInfo = ref(null)

const discovering = ref(false)
const discoveryError = ref('')
const result = ref(null)

async function unlockDiscovery() {
  authError.value = ''
  authenticating.value = true

  try {
    networkInfo.value = await getNetworkInfo(
      discoveryKey.value,
    )

    authenticated.value = true
  } catch (error) {
    authenticated.value = false
    networkInfo.value = null

    if (error.status === 401 || error.status === 403) {
      authError.value = 'Invalid discovery password.'
    } else if (error.status === 503) {
      authError.value =
        'Network discovery is not configured.'
    } else {
      authError.value =
        error.message || 'Unable to unlock discovery.'
    }
  } finally {
    authenticating.value = false
  }
}

async function handleDiscover({
  startIp,
  endIp,
}) {
  discoveryError.value = ''
  result.value = null
  discovering.value = true

  try {
    result.value = await discoverNetwork(
      discoveryKey.value,
      startIp,
      endIp,
    )
  } catch (error) {
    if (error.status === 401 || error.status === 403) {
      discoveryError.value =
        error.message || 'Discovery request denied.'
    } else if (error.status === 422) {
      discoveryError.value =
        error.message || 'Invalid IP range.'
    } else if (error.status === 429) {
      discoveryError.value =
        'Too many discovery requests. Try again later.'
    } else {
      discoveryError.value =
        error.message || 'Network discovery failed.'
    }
  } finally {
    discovering.value = false
  }
}

function lockDiscovery() {
  discoveryKey.value = ''
  authenticated.value = false
  networkInfo.value = null
  result.value = null
  authError.value = ''
  discoveryError.value = ''
}
</script>

<template>
  <section class="card network-discovery">
    <div class="card-header monitor-heading">
      <div>
        <h2>Network Discovery</h2>

        <p>
          Discover reachable hosts on your internal
          network.
        </p>
      </div>

      <span
        class="badge"
        :class="{ inactive: !authenticated }"
      >
        {{ authenticated ? 'Unlocked' : 'Locked' }}
      </span>
    </div>

    <form
      v-if="!authenticated"
      class="network-auth-form"
      @submit.prevent="unlockDiscovery"
    >
      <div class="field">
        <label for="discovery-password">
          Discovery password
        </label>

        <input
          id="discovery-password"
          v-model="discoveryKey"
          type="password"
          autocomplete="current-password"
          placeholder="Enter discovery password"
          required
        >
      </div>

      <button
        type="submit"
        :disabled="authenticating"
      >
        {{
          authenticating
            ? 'Unlocking...'
            : 'Unlock Network Discovery'
        }}
      </button>

      <p
        v-if="authError"
        class="error"
      >
        {{ authError }}
      </p>
    </form>

    <template v-else>
      <NetworkInfo
        :host-ip="networkInfo?.host_ip"
        :scanner-ip="networkInfo?.scanner_ip"
      />

      <NetworkScanForm
        :disabled="discovering"
        @discover="handleDiscover"
      />

      <p
        v-if="discoveryError"
        class="error network-discovery-error"
      >
        {{ discoveryError }}
      </p>

      <NetworkResults
        v-if="result"
        :result="result"
      />

      <button
        class="network-lock-button"
        type="button"
        :disabled="discovering"
        @click="lockDiscovery"
      >
        Lock Discovery
      </button>
    </template>
  </section>
</template>