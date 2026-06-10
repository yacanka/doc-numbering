// src/stores/preferences.ts
import { computed, ref, watch } from 'vue'
import { defineStore } from 'pinia'
import type { InterfaceDensity, ThemePreference } from '@/types'

const THEME_STORAGE_KEY = 'docnumber_theme'
const DENSITY_STORAGE_KEY = 'docnumber_density'

function readThemePreference(): ThemePreference {
  const storedTheme = localStorage.getItem(THEME_STORAGE_KEY)
  return storedTheme === 'dark' ? 'dark' : 'light'
}

function readInterfaceDensity(): InterfaceDensity {
  const storedDensity = localStorage.getItem(DENSITY_STORAGE_KEY)
  return storedDensity === 'compact' ? 'compact' : 'comfortable'
}

export const usePreferencesStore = defineStore('preferences', () => {
  const theme = ref<ThemePreference>(readThemePreference())
  const density = ref<InterfaceDensity>(readInterfaceDensity())
  const isDarkTheme = computed(() => theme.value === 'dark')
  const componentSize = computed(() => density.value === 'compact' ? 'small' : 'medium')

  watch(theme, (nextTheme) => {
    localStorage.setItem(THEME_STORAGE_KEY, nextTheme)
    document.documentElement.dataset.theme = nextTheme
  }, { immediate: true })

  watch(density, (nextDensity) => {
    localStorage.setItem(DENSITY_STORAGE_KEY, nextDensity)
  }, { immediate: true })

  function setTheme(nextTheme: ThemePreference) {
    theme.value = nextTheme
  }

  function setDensity(nextDensity: InterfaceDensity) {
    density.value = nextDensity
  }

  return { theme, density, isDarkTheme, componentSize, setTheme, setDensity }
})
