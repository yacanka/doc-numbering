<!-- src/App.vue -->
<script setup lang="ts">
import { computed } from 'vue'
import { NConfigProvider, NDialogProvider, NGlobalStyle, NMessageProvider, darkTheme } from 'naive-ui'
import { usePreferencesStore } from '@/stores/preferences'

const preferencesStore = usePreferencesStore()
const activeTheme = computed(() => preferencesStore.isDarkTheme ? darkTheme : null)
const themeOverrides = {
  common: {
    primaryColor: '#1890FF',
    primaryColorHover: '#40A9FF',
    primaryColorPressed: '#096DD9',
  },
}
</script>

<template>
  <n-config-provider
    :theme="activeTheme"
    :theme-overrides="themeOverrides"
    :component-size="preferencesStore.componentSize"
  >
    <n-global-style />
    <n-message-provider>
      <n-dialog-provider>
        <RouterView />
      </n-dialog-provider>
    </n-message-provider>
  </n-config-provider>
</template>
