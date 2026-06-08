<!-- src/views/FormatsView.vue -->
<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import {
  NCard, NButton, NSpace, NText, NInput, NSelect,
  NTag, NEmpty, NSpin, NGrid, NGi, NIcon,
  NDropdown, NPopconfirm, useMessage, NTabs, NTab,
  NBadge,
} from 'naive-ui'
import {
  AddOutline, SearchOutline, FilterOutline,
  CreateOutline, CopyOutline, TrashOutline,
  PlayOutline, EllipsisHorizontalOutline,
} from '@vicons/ionicons5'
import { useFormatsStore } from '@/stores/formats'
import { formatsApi } from '@/api/formats'
import type { DocumentFormat } from '@/types'
import GenerateModal from '@/components/document/GenerateModal.vue'

const router = useRouter()
const message = useMessage()
const store = useFormatsStore()

const searchQuery = ref('')
const statusFilter = ref<string | null>(null)
const categoryFilter = ref<string | null>(null)
const generating = ref<string | null>(null)
const showGenerateModal = ref(false)
const selectedFormat = ref<DocumentFormat | null>(null)

const statusOptions = [
  { label: 'Tümü', value: null },
  { label: 'Aktif', value: 'active' },
  { label: 'Taslak', value: 'draft' },
  { label: 'Kullanım Dışı', value: 'deprecated' },
]

const categoryOptions = computed(() => [
  { label: 'Tüm Kategoriler', value: null },
  ...store.categories.map((c) => ({ label: c.name, value: c.id })),
])

onMounted(async () => {
  await Promise.all([
    store.fetchFormats(),
    store.fetchCategories(),
  ])
})

const filteredFormats = computed(() => {
  return store.formats.filter((f) => {
    if (searchQuery.value) {
      const q = searchQuery.value.toLowerCase()
      if (!f.name.toLowerCase().includes(q) && !f.code.toLowerCase().includes(q)) {
        return false
      }
    }
    if (statusFilter.value && f.status !== statusFilter.value) return false
    if (categoryFilter.value && f.category !== categoryFilter.value) return false
    return true
  })
})

function getStatusTag(status: string) {
  const map: Record<string, { type: any; label: string }> = {
    active: { type: 'success', label: 'Aktif' },
    draft: { type: 'default', label: 'Taslak' },
    deprecated: { type: 'warning', label: 'Kullanım Dışı' },
    archived: { type: 'error', label: 'Arşivlendi' },
  }
  return map[status] || { type: 'default', label: status }
}

function openGenerate(format: DocumentFormat) {
  selectedFormat.value = format
  showGenerateModal.value = true
}

function getFormatActions(format: DocumentFormat) {
  return [
    {
      label: 'Düzenle',
      key: 'edit',
      icon: () => h(NIcon, null, { default: () => h(CreateOutline) }),
    },
    {
      label: 'Kopyala',
      key: 'duplicate',
      icon: () => h(NIcon, null, { default: () => h(CopyOutline) }),
    },
    { type: 'divider', key: 'd1' },
    format.status === 'active'
      ? { label: 'Devre Dışı Bırak', key: 'deactivate' }
      : { label: 'Aktifleştir', key: 'activate' },
    { type: 'divider', key: 'd2' },
    {
      label: 'Sil',
      key: 'delete',
      props: { style: { color: 'red' } },
    },
  ]
}

async function handleFormatAction(key: string, format: DocumentFormat) {
  switch (key) {
    case 'edit':
      router.push(`/formats/${format.id}/edit`)
      break
    case 'duplicate':
      try {
        await store.duplicateFormat(format.id)
        message.success('Format kopyalandı')
      } catch {
        message.error('Kopyalama hatası')
      }
      break
    case 'activate':
      await store.activateFormat(format.id)
      message.success('Format aktifleştirildi')
      break
    case 'deactivate':
      await store.deactivateFormat(format.id)
      message.success('Format devre dışı bırakıldı')
      break
    case 'delete':
      try {
        await store.deleteFormat(format.id)
        message.success('Format silindi')
      } catch (err: any) {
        message.error(err.response?.data?.error?.message || 'Silme hatası')
      }
      break
  }
}

import { h } from 'vue'
</script>

<template>
  <div>
    <!-- Header -->
    <n-space align="center" justify="space-between" style="margin-bottom: 24px">
      <div>
        <n-text tag="h1" style="margin: 0; font-size: 24px; font-weight: 600">
          Format Yönetimi
        </n-text>
        <n-text depth="3">
          {{ store.formats.length }} format tanımlanmış,
          {{ store.activeFormats.length }} aktif
        </n-text>
      </div>
      <n-button
        type="primary"
        @click="router.push('/formats/new')"
      >
        <template #icon><n-icon :component="AddOutline" /></template>
        Yeni Format
      </n-button>
    </n-space>

    <!-- Filters -->
    <n-card style="margin-bottom: 16px" size="small">
      <n-space>
        <n-input
          v-model:value="searchQuery"
          placeholder="Format ara..."
          clearable
          style="width: 240px"
        >
          <template #prefix>
            <n-icon :component="SearchOutline" />
          </template>
        </n-input>

        <n-select
          v-model:value="statusFilter"
          :options="statusOptions"
          style="width: 160px"
          placeholder="Durum"
        />

        <n-select
          v-model:value="categoryFilter"
          :options="categoryOptions"
          style="width: 200px"
          placeholder="Kategori"
          clearable
        />
      </n-space>
    </n-card>

    <!-- Formats Grid -->
    <n-spin :show="store.loading">
      <template v-if="filteredFormats.length">
        <n-grid :cols="3" :x-gap="16" :y-gap="16" responsive="screen" :item-responsive="true">
          <n-gi
            v-for="format in filteredFormats"
            :key="format.id"
            span="3 m:3 l:1"
          >
            <n-card
              size="small"
              hoverable
              class="format-card"
            >
              <template #header>
                <n-space align="center" justify="space-between">
                  <n-space align="center" size="small">
                    <n-tag
                      :type="getStatusTag(format.status).type"
                      size="tiny"
                    >
                      {{ getStatusTag(format.status).label }}
                    </n-tag>
                    <n-text
                      strong
                      style="font-family: monospace; font-size: 12px; color: #1890ff"
                    >
                      {{ format.code }}
                    </n-text>
                  </n-space>

                  <n-dropdown
                    :options="getFormatActions(format)"
                    @select="(key: string) => handleFormatAction(key, format)"
                    trigger="click"
                  >
                    <n-button text size="small">
                      <template #icon>
                        <n-icon :component="EllipsisHorizontalOutline" />
                      </template>
                    </n-button>
                  </n-dropdown>
                </n-space>
              </template>

              <!-- Format Name -->
              <n-text strong style="font-size: 15px; display: block; margin-bottom: 6px">
                {{ format.name }}
              </n-text>

              <n-text depth="3" style="font-size: 12px; display: block; margin-bottom: 12px">
                {{ format.description || 'Açıklama yok' }}
              </n-text>

              <!-- Preview -->
              <div class="format-preview-box">
                {{ format.preview || '...' }}
              </div>

              <!-- Stats -->
              <n-space style="margin-top: 12px" size="small">
                <n-text depth="3" style="font-size: 12px">
                  📊 {{ format.total_generated?.toLocaleString() || 0 }} belge
                </n-text>
                <n-text depth="3" style="font-size: 12px">
                  🔄 {{ format.sequence_reset_period }}
                </n-text>
              </n-space>

              <!-- Actions -->
              <n-space style="margin-top: 12px">
                <n-button
                  size="small"
                  type="primary"
                  :disabled="format.status !== 'active'"
                  @click="openGenerate(format)"
                >
                  <template #icon><n-icon :component="PlayOutline" /></template>
                  Oluştur
                </n-button>
                <n-button
                  size="small"
                  @click="router.push(`/formats/${format.id}/edit`)"
                >
                  <template #icon><n-icon :component="CreateOutline" /></template>
                  Düzenle
                </n-button>
              </n-space>
            </n-card>
          </n-gi>
        </n-grid>
      </template>

      <n-empty
        v-else
        description="Format bulunamadı"
        style="padding: 60px"
      >
        <template #extra>
          <n-button
            type="primary"
            @click="router.push('/formats/new')"
          >
            İlk Formatı Oluştur
          </n-button>
        </template>
      </n-empty>
    </n-spin>

    <!-- Generate Modal -->
    <generate-modal
      v-if="showGenerateModal && selectedFormat"
      :format="selectedFormat"
      v-model:show="showGenerateModal"
    />
  </div>
</template>

<style scoped>
.format-card {
  transition: transform 0.2s;
}

.format-card:hover {
  transform: translateY(-2px);
}

.format-preview-box {
  background: #001529;
  color: #52e52e;
  font-family: 'Courier New', monospace;
  font-size: 14px;
  font-weight: 600;
  letter-spacing: 2px;
  padding: 10px 14px;
  border-radius: 6px;
  word-break: break-all;
  min-height: 40px;
}
</style>