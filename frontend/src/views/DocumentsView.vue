<!-- src/views/DocumentsView.vue -->
<script setup lang="ts">
import { computed, h, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import {
  NButton, NCard, NDataTable, NInput, NSelect, NSpace,
  NStatistic, NTag, NText, useMessage, type DataTableColumns,
} from 'naive-ui'
import { documentsApi, type DocumentFilters } from '@/api/documents'
import { useFormatsStore } from '@/stores/formats'
import type { GeneratedDocument } from '@/types'

const route = useRoute()
const message = useMessage()
const formatsStore = useFormatsStore()

const documents = ref<GeneratedDocument[]>([])
const loading = ref(false)
const searchQuery = ref('')
const statusFilter = ref('all')
const formatFilter = ref<string | null>(null)
const pagination = ref({ page: 1, pageSize: 20, itemCount: 0 })

const statusOptions = [
  { label: 'Tümü', value: 'all' },
  { label: 'Aktif', value: 'active' },
  { label: 'Kullanıldı', value: 'used' },
  { label: 'İptal', value: 'cancelled' },
  { label: 'Süresi Doldu', value: 'expired' },
]

const formatOptions = computed(() =>
  formatsStore.formats.map((format) => ({ label: `${format.code} - ${format.name}`, value: format.id }))
)

const columns: DataTableColumns<GeneratedDocument> = [
  { title: 'Numara', key: 'document_number', render: renderDocumentNumber },
  { title: 'Format', key: 'format_name', render: renderFormat },
  { title: 'Durum', key: 'status', render: renderStatus },
  { title: 'Sıra', key: 'sequence_value', width: 90 },
  { title: 'Oluşturan', key: 'generated_by_username' },
  { title: 'Oluşturulma', key: 'generated_at', render: renderDate },
]

onMounted(async () => {
  await formatsStore.fetchFormats()
  syncFiltersFromRoute()
  await fetchDocuments()
})

watch([searchQuery, statusFilter, formatFilter], () => {
  pagination.value.page = 1
  fetchDocuments()
})

function syncFiltersFromRoute() {
  const format = route.query.format
  formatFilter.value = typeof format === 'string' ? format : null
}

function buildFilters(): DocumentFilters {
  return {
    page: pagination.value.page,
    page_size: pagination.value.pageSize,
    search: searchQuery.value || undefined,
    format: formatFilter.value || undefined,
    status: statusFilter.value === 'all' ? undefined : statusFilter.value,
  }
}

async function fetchDocuments() {
  loading.value = true
  try {
    const response = await documentsApi.getDocuments(buildFilters())
    documents.value = response.data.data
    pagination.value.itemCount = response.data.pagination.count
  } catch (err: any) {
    message.error(err.response?.data?.error?.message || 'Belge numaraları alınamadı')
  } finally {
    loading.value = false
  }
}

function handlePageChange(page: number) {
  pagination.value.page = page
  fetchDocuments()
}

function handlePageSizeChange(pageSize: number) {
  pagination.value.page = 1
  pagination.value.pageSize = pageSize
  fetchDocuments()
}

function renderDocumentNumber(row: GeneratedDocument) {
  return h(NText, { strong: true, style: 'font-family: monospace; letter-spacing: 1px' }, {
    default: () => row.document_number,
  })
}

function renderFormat(row: GeneratedDocument) {
  return h('div', [
    h(NText, { strong: true }, { default: () => row.format_code }),
    h('br'),
    h(NText, { depth: 3, style: 'font-size: 12px' }, { default: () => row.format_name }),
  ])
}

function renderStatus(row: GeneratedDocument) {
  const status = getStatusTag(row.status)
  return h(NTag, { type: status.type, size: 'small' }, { default: () => status.label })
}

function renderDate(row: GeneratedDocument) {
  return new Date(row.generated_at).toLocaleString('tr-TR')
}

function getStatusTag(status: GeneratedDocument['status']) {
  const map = {
    active: { type: 'success' as const, label: 'Aktif' },
    used: { type: 'info' as const, label: 'Kullanıldı' },
    cancelled: { type: 'error' as const, label: 'İptal' },
    expired: { type: 'warning' as const, label: 'Süresi Doldu' },
  }
  return map[status] || { type: 'default' as const, label: status }
}
</script>

<template>
  <div>
    <n-space align="center" justify="space-between" style="margin-bottom: 24px">
      <div>
        <n-text tag="h1" style="margin: 0; font-size: 24px; font-weight: 600">
          Belgeler
        </n-text>
        <n-text depth="3">Oluşturulan belge numaralarını buradan takip edebilirsiniz.</n-text>
      </div>
      <n-statistic label="Toplam" :value="pagination.itemCount" />
    </n-space>

    <n-card size="small" style="margin-bottom: 16px">
      <n-space>
        <n-input v-model:value="searchQuery" clearable placeholder="Numara ara..." style="width: 240px" />
        <n-select v-model:value="statusFilter" :options="statusOptions" style="width: 160px" />
        <n-select
          v-model:value="formatFilter"
          :options="formatOptions"
          clearable
          filterable
          placeholder="Format seçin"
          style="width: 280px"
        />
        <n-button :loading="loading" @click="fetchDocuments">Yenile</n-button>
      </n-space>
    </n-card>

    <n-card>
      <n-data-table
        remote
        :columns="columns"
        :data="documents"
        :loading="loading"
        :pagination="{
          page: pagination.page,
          pageSize: pagination.pageSize,
          itemCount: pagination.itemCount,
          showSizePicker: true,
          pageSizes: [10, 20, 50, 100],
          onChange: handlePageChange,
          onUpdatePageSize: handlePageSizeChange,
        }"
      />
    </n-card>
  </div>
</template>
