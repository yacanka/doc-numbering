<!-- src/components/format/SegmentPalette.vue -->
<script setup lang="ts">
import { NGrid, NGi, NCard, NText, NIcon, NTooltip } from 'naive-ui'
import type { SegmentTypeInfo } from '@/types'

const props = defineProps<{
  segmentTypes: SegmentTypeInfo[]
}>()

const emit = defineEmits<{
  add: [type: string]
}>()

const segmentColors: Record<string, string> = {
  static: '#8c8c8c',
  date: '#1890ff',
  sequence: '#52c41a',
  yearly_sequence: '#87d068',
  random: '#faad14',
  checksum: '#f5222d',
  context: '#722ed1',
  separator: '#bfbfbf',
}

const segmentEmojis: Record<string, string> = {
  static: '📝',
  date: '📅',
  sequence: '🔢',
  yearly_sequence: '🔄',
  random: '🎲',
  checksum: '✅',
  context: '🏷️',
  separator: '➖',
}
</script>

<template>
  <n-grid :cols="2" :x-gap="8" :y-gap="8">
    <n-gi v-for="seg in segmentTypes" :key="seg.type">
      <n-tooltip :delay="500">
        <template #trigger>
          <div
            class="segment-palette-item"
            :style="{ borderColor: segmentColors[seg.type] }"
            @click="emit('add', seg.type)"
          >
            <span class="seg-emoji">{{ segmentEmojis[seg.type] }}</span>
            <n-text style="font-size: 12px; text-align: center">
              {{ seg.label }}
            </n-text>
          </div>
        </template>
        {{ seg.description }}
      </n-tooltip>
    </n-gi>
  </n-grid>
</template>

<style scoped>
.segment-palette-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 10px 8px;
  border: 2px solid #f0f0f0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  background: white;
  min-height: 64px;
}

.segment-palette-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.seg-emoji {
  font-size: 20px;
}
</style>