<!-- src/views/DocumentsView.vue -->
<script setup lang="ts">
import { NAlert, NCard, NText } from 'naive-ui'
</script>

<template>
  <n-card>
    <n-text tag="h1" style="margin: 0 0 12px; font-size: 24px; font-weight: 600">
      Belgeler
    </n-text>
    <n-alert type="info" title="Belge listesi hazırlanıyor">
      Oluşturulan belge numaraları format kartlarındaki Oluştur aksiyonu üzerinden üretilebilir.
    </n-alert>
  </n-card>
</template>
