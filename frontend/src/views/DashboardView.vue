<!-- src/views/DashboardView.vue -->
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import {
  NGrid, NGi, NStatistic, NCard, NSpin, NNumberAnimation,
  NSpace, NText, NIcon, NTag, NEmpty,
  NList, NListItem, NThing,
} from 'naive-ui'
import {
  DocumentTextOutline, CheckmarkCircleOutline,
  TodayOutline, CalendarOutline, GridOutline,
} from '@vicons/ionicons5'
import { formatsApi } from '@/api/formats'
import { documentsApi } from '@/api/documents'
import type { DashboardStats, DocumentStats } from '@/types'
import { useRouter } from 'vue-router'

const router = useRouter()
const loading = ref(false)
const formatStats = ref<DashboardStats | null>(null)
const docStats = ref<DocumentStats | null>(null)

async function loadStats() {
  loading.value = true
  try {
    const [fRes, dRes] = await Promise.all([
      formatsApi.getStats(),
      documentsApi.getStats(),
    ])
    formatStats.value = fRes.data.data
    docStats.value = dRes.data.data
  } finally {
    loading.value = false
  }
}

onMounted(loadStats)
</script>

<template>
  <div>
    <n-space vertical size="large">
      <!-- Page Title -->
      <div>
        <n-text tag="h1" style="margin: 0; font-size: 24px; font-weight: 600">
          Dashboard
        </n-text>
        <n-text depth="3">Belge numarası sistemi genel durumu</n-text>
      </div>

      <!-- Stats Cards -->
      <n-spin :show="loading">
        <n-grid :cols="4" :x-gap="16" :y-gap="16" responsive="screen" :item-responsive="true">
          <n-gi span="4 m:2 l:1">
            <n-card>
              <n-statistic label="Toplam Format">
                <template #prefix>
                  <n-icon :component="GridOutline" color="#1890ff" />
                </template>
                <n-number-animation :from="0" :to="formatStats?.total_formats || 0" />
              </n-statistic>
              <div style="margin-top: 8px">
                <n-tag type="success" size="small">
                  {{ formatStats?.active_formats || 0 }} Aktif
                </n-tag>
              </div>
            </n-card>
          </n-gi>

          <n-gi span="4 m:2 l:1">
            <n-card>
              <n-statistic label="Toplam Belge">
                <template #prefix>
                  <n-icon :component="DocumentTextOutline" color="#52c41a" />
                </template>
                <n-number-animation :from="0" :to="docStats?.total_generated || 0" />
              </n-statistic>
              <div style="margin-top: 8px">
                <n-tag type="info" size="small">
                  {{ docStats?.active_count || 0 }} Aktif
                </n-tag>
              </div>
            </n-card>
          </n-gi>

          <n-gi span="4 m:2 l:1">
            <n-card>
              <n-statistic label="Bugün Oluşturulan">
                <template #prefix>
                  <n-icon :component="TodayOutline" color="#faad14" />
                </template>
                <n-number-animation :from="0" :to="docStats?.today_count || 0" />
              </n-statistic>
              <div style="margin-top: 8px">
                <n-tag size="small">Bu Hafta: {{ docStats?.this_week_count || 0 }}</n-tag>
              </div>
            </n-card>
          </n-gi>

          <n-gi span="4 m:2 l:1">
            <n-card>
              <n-statistic label="Bu Ay">
                <template #prefix>
                  <n-icon :component="CalendarOutline" color="#722ed1" />
                </template>
                <n-number-animation :from="0" :to="docStats?.this_month_count || 0" />
              </n-statistic>
              <div style="margin-top: 8px">
                <n-tag type="warning" size="small">
                  {{ docStats?.cancelled_count || 0 }} İptal
                </n-tag>
              </div>
            </n-card>
          </n-gi>
        </n-grid>

        <!-- Bottom Row -->
        <n-grid :cols="2" :x-gap="16" :y-gap="16" style="margin-top: 16px" responsive="screen" :item-responsive="true">
          <!-- Top Formats -->
          <n-gi span="2 l:1">
            <n-card title="En Çok Kullanılan Formatlar">
              <template #header-extra>
                <n-text
                  tag="a"
                  style="cursor: pointer; color: #1890ff"
                  @click="router.push('/formats')"
                >
                  Tümünü Gör
                </n-text>
              </template>

              <template v-if="docStats?.by_format?.length">
                <n-list>
                  <n-list-item
                    v-for="item in docStats.by_format.slice(0, 5)"
                    :key="item.format__code"
                  >
                    <n-thing :title="item.format__name">
                      <template #description>
                        <n-tag size="small" style="font-family: monospace">
                          {{ item.format__code }}
                        </n-tag>
                      </template>
                      <template #header-extra>
                        <n-text strong style="color: #1890ff">
                          {{ item.count.toLocaleString() }}
                        </n-text>
                      </template>
                    </n-thing>
                  </n-list-item>
                </n-list>
              </template>
              <n-empty v-else description="Henüz veri yok" />
            </n-card>
          </n-gi>

          <!-- Recent Activity -->
          <n-gi span="2 l:1">
            <n-card title="Günlük Aktivite (Son 30 Gün)">
              <template v-if="docStats?.daily_trend?.length">
                <div style="overflow-x: auto">
                  <div class="activity-chart">
                    <div
                      v-for="item in docStats.daily_trend.slice(-14)"
                      :key="item.date"
                      class="activity-bar"
                    >
                      <div
                        class="bar"
                        :style="{
                          height: `${Math.min(100, (item.count / Math.max(...docStats!.daily_trend.map(d => d.count))) * 100)}px`,
                          background: '#1890ff'
                        }"
                        :title="`${item.date}: ${item.count}`"
                      />
                      <span class="date-label">{{ item.date.slice(5) }}</span>
                    </div>
                  </div>
                </div>
              </template>
              <n-empty v-else description="Henüz aktivite yok" />
            </n-card>
          </n-gi>
        </n-grid>
      </n-spin>
    </n-space>
  </div>
</template>

<style scoped>
.activity-chart {
  display: flex;
  align-items: flex-end;
  gap: 6px;
  height: 120px;
  padding: 0 4px;
}

.activity-bar {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
  gap: 4px;
}

.bar {
  width: 100%;
  min-height: 4px;
  border-radius: 2px 2px 0 0;
  transition: height 0.3s ease;
}

.date-label {
  font-size: 10px;
  color: #8c8c8c;
  white-space: nowrap;
  transform: rotate(-45deg);
  display: block;
  width: 20px;
}
</style>