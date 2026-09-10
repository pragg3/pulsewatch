<script setup>
import '../../assets/styles/network-info.css'

defineProps({
  clientIp: {
    type: String,
    default: null,
  },
  scannerIp: {
    type: String,
    default: null,
  },
})
</script>

<template>
  <div class="network-info">
    <div class="network-info-item">
      <span class="network-info-label">
        Detected client IP
      </span>

      <strong>
        {{ clientIp || 'Unavailable' }}
      </strong>
    </div>

    <div class="network-info-item">
      <span class="network-info-label">
        Scanner IP
      </span>

      <strong>
        {{ scannerIp || 'Unavailable' }}
      </strong>
    </div>
  </div>
</template>