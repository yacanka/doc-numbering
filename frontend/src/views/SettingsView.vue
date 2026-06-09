<!-- src/views/SettingsView.vue -->
<script setup lang="ts">
import { NAlert, NCard, NText } from 'naive-ui'
</script>

<template>
  <n-card>
    <n-text tag="h1" style="margin: 0 0 12px; font-size: 24px; font-weight: 600">
      Ayarlar
    </n-text>
    <n-alert type="info" title="Ayarlar yakında">
      Sistem ayarları bu alanda yönetilecektir.
    </n-alert>
  </n-card>
</template>
