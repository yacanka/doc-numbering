<!-- src/views/SettingsView.vue -->
<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import type { FormInst, FormRules } from 'naive-ui'
import {
  NAlert,
  NButton,
  NCard,
  NForm,
  NFormItem,
  NGrid,
  NGridItem,
  NInput,
  NRadioButton,
  NRadioGroup,
  NSpace,
  NText,
  useMessage,
} from 'naive-ui'
import { useAuthStore } from '@/stores/auth'
import { usePreferencesStore } from '@/stores/preferences'
import type { InterfaceDensity, ThemePreference, UserProfileUpdate } from '@/types'

const message = useMessage()
const authStore = useAuthStore()
const preferencesStore = usePreferencesStore()
const profileFormReference = ref<FormInst | null>(null)
const savingProfile = ref(false)
const profileForm = reactive<UserProfileUpdate>({ email: '', first_name: '', last_name: '' })
const username = computed(() => authStore.user?.username || '-')

const profileRules: FormRules = {
  email: [
    { required: true, message: 'E-posta adresi zorunludur.', trigger: ['blur', 'input'] },
    { type: 'email', message: 'Geçerli bir e-posta adresi girin.', trigger: ['blur', 'input'] },
  ],
  first_name: { max: 150, message: 'Ad en fazla 150 karakter olabilir.', trigger: 'input' },
  last_name: { max: 150, message: 'Soyad en fazla 150 karakter olabilir.', trigger: 'input' },
}

const hasProfileChanges = computed(() => {
  const user = authStore.user
  if (!user) return false
  return profileForm.email !== user.email
    || profileForm.first_name !== user.first_name
    || profileForm.last_name !== user.last_name
})

watch(() => authStore.user, fillProfileForm, { immediate: true })

function fillProfileForm() {
  profileForm.email = authStore.user?.email || ''
  profileForm.first_name = authStore.user?.first_name || ''
  profileForm.last_name = authStore.user?.last_name || ''
}

async function saveProfile() {
  try {
    await profileFormReference.value?.validate()
    savingProfile.value = true
    await authStore.updateProfile({ ...profileForm })
    message.success('Profil ayarları güncellendi.')
  } catch {
    if (savingProfile.value) message.error('Profil güncellenemedi. Lütfen bilgileri kontrol edin.')
  } finally {
    savingProfile.value = false
  }
}

function selectTheme(nextTheme: ThemePreference) {
  preferencesStore.setTheme(nextTheme)
  message.success(`${nextTheme === 'dark' ? 'Koyu' : 'Açık'} tema etkinleştirildi.`)
}

function selectDensity(nextDensity: InterfaceDensity) {
  preferencesStore.setDensity(nextDensity)
  message.success('Arayüz yoğunluğu güncellendi.')
}
</script>

<template>
  <n-space vertical size="large">
    <div>
      <n-text tag="h1" class="page-title">Ayarlar</n-text>
      <n-text depth="3">Profil, tema ve kullanım tercihlerinizi buradan yönetin.</n-text>
    </div>

    <n-grid :cols="2" :x-gap="20" :y-gap="20" responsive="screen">
      <n-grid-item>
        <n-card title="Profil Ayarları" :bordered="false">
          <n-alert type="info" title="Kullanıcı adı korunur" style="margin-bottom: 16px">
            Güvenlik ve denetlenebilirlik için kullanıcı adı bu ekrandan değiştirilemez.
          </n-alert>
          <n-form
            ref="profileFormReference"
            :model="profileForm"
            :rules="profileRules"
            label-placement="top"
            @submit.prevent="saveProfile"
          >
            <n-form-item label="Kullanıcı adı">
              <n-input :value="username" disabled />
            </n-form-item>
            <n-form-item label="E-posta" path="email">
              <n-input v-model:value="profileForm.email" autocomplete="email" />
            </n-form-item>
            <n-form-item label="Ad" path="first_name">
              <n-input v-model:value="profileForm.first_name" autocomplete="given-name" />
            </n-form-item>
            <n-form-item label="Soyad" path="last_name">
              <n-input v-model:value="profileForm.last_name" autocomplete="family-name" />
            </n-form-item>
            <n-space justify="end">
              <n-button :disabled="!hasProfileChanges" @click="fillProfileForm">Vazgeç</n-button>
              <n-button
                type="primary"
                attr-type="submit"
                :loading="savingProfile"
                :disabled="!hasProfileChanges"
              >
                Profili Güncelle
              </n-button>
            </n-space>
          </n-form>
        </n-card>
      </n-grid-item>

      <n-grid-item>
        <n-space vertical size="large">
          <n-card title="Tema" :bordered="false">
            <n-text depth="3">Göz konforu için açık veya koyu tema seçin.</n-text>
            <n-radio-group
              :value="preferencesStore.theme"
              style="margin-top: 16px"
              @update:value="selectTheme"
            >
              <n-radio-button value="light">Light</n-radio-button>
              <n-radio-button value="dark">Dark</n-radio-button>
            </n-radio-group>
          </n-card>

          <n-card title="Arayüz Yoğunluğu" :bordered="false">
            <n-text depth="3">Tablo ve formlarda daha kompakt bir görünüm tercih edebilirsiniz.</n-text>
            <n-radio-group
              :value="preferencesStore.density"
              style="margin-top: 16px"
              @update:value="selectDensity"
            >
              <n-radio-button value="comfortable">Rahat</n-radio-button>
              <n-radio-button value="compact">Kompakt</n-radio-button>
            </n-radio-group>
          </n-card>
        </n-space>
      </n-grid-item>
    </n-grid>
  </n-space>
</template>

<style scoped>
.page-title {
  display: block;
  margin: 0 0 8px;
  font-size: 24px;
  font-weight: 600;
}
</style>
