<script setup>
import '../../assets/styles/network-results.css'

defineProps({
  result: {
    type: Object,
    required: true,
  },
})
</script>

<template>
  <div class="network-results">
    <div class="network-summary">
      <div class="network-summary-item">
        <span>Addresses checked</span>
        <strong>{{ result.requested_hosts }}</strong>
      </div>

      <div class="network-summary-item">
        <span>Reachable hosts</span>
        <strong>{{ result.reachable_hosts }}</strong>
      </div>
    </div>

    <div
      v-if="result.hosts.length === 0"
      class="empty-state"
    >
      <h3>No reachable hosts found</h3>

      <p>
        No responding hosts were found in the
        selected range.
      </p>
    </div>

    <div
      v-else
      class="network-host-list"
    >
      <article
        v-for="host in result.hosts"
        :key="host.ip"
        class="network-host"
      >
        <div class="monitor-info">
          <span class="monitor-dot" />

          <div>
            <h3>
              {{ host.hostname || 'Unknown host' }}
            </h3>

            <span class="network-host-ip">
              {{ host.ip }}
            </span>
          </div>
        </div>

        <span class="badge">
          Reachable
        </span>
      </article>
    </div>
  </div>
</template>