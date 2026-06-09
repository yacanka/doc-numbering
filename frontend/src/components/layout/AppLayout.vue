<!-- src/components/layout/AppLayout.vue -->
<script setup lang="ts">
import { h, ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  NLayout, NLayoutSider, NLayoutContent, NLayoutHeader,
  NMenu, NIcon, NText, NAvatar, NDropdown, NSpace,
  NBreadcrumb, NBreadcrumbItem, NSwitch, NTag,
} from 'naive-ui'
import {
  GridOutline, DocumentTextOutline, SettingsOutline,
  BarChartOutline, LogOutOutline, PersonOutline,
  ChevronDownOutline,
} from '@vicons/ionicons5'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const collapsed = ref(false)
const menuThemeOverrides = {
  itemColorActiveCollapsed: 'rgba(24, 144, 255, 0.15)',
}

const menuOptions = [
  {
    label: 'Dashboard',
    key: '/',
    icon: () => h(NIcon, null, { default: () => h(BarChartOutline) }),
  },
  {
    label: 'Format Yönetimi',
    key: '/formats',
    icon: () => h(NIcon, null, { default: () => h(GridOutline) }),
  },
  {
    label: 'Belgeler',
    key: '/documents',
    icon: () => h(NIcon, null, { default: () => h(DocumentTextOutline) }),
  },
  {
    label: 'Ayarlar',
    key: '/settings',
    icon: () => h(NIcon, null, { default: () => h(SettingsOutline) }),
  },
]

const activeKey = computed(() => route.path)

function handleMenuSelect(key: string) {
  router.push(key)
}

const userDropdownOptions = [
  { label: 'Profil', key: 'profile', icon: () => h(NIcon, null, { default: () => h(PersonOutline) }) },
  { type: 'divider', key: 'd1' },
  { label: 'Çıkış Yap', key: 'logout', icon: () => h(NIcon, null, { default: () => h(LogOutOutline) }) },
]

function handleUserAction(key: string) {
  if (key === 'logout') {
    authStore.logout()
    router.push('/login')
  }
}
</script>

<template>
  <n-layout has-sider style="height: 100vh">
    <!-- Sidebar -->
    <n-layout-sider
      bordered
      collapse-mode="width"
      :collapsed-width="64"
      :width="240"
      :collapsed="collapsed"
      show-trigger
      @collapse="collapsed = true"
      @expand="collapsed = false"
      style="background: #001529"
    >
      <!-- Logo -->
      <div class="sidebar-logo" :class="{ collapsed }">
        <div class="logo-icon">📋</div>
        <Transition name="fade">
          <n-text v-if="!collapsed" strong style="color: white; font-size: 16px; white-space: nowrap">
            DocNumber
          </n-text>
        </Transition>
      </div>

      <n-menu
        :collapsed="collapsed"
        :collapsed-width="64"
        :collapsed-icon-size="24"
        :options="menuOptions"
        :value="activeKey"
        @update:value="handleMenuSelect"
        :root-indent="18"
        :theme-overrides="menuThemeOverrides"
      />
    </n-layout-sider>

    <!-- Main Content Area -->
    <n-layout>
      <!-- Header -->
      <n-layout-header
        bordered
        style="height: 64px; padding: 0 24px; display: flex; align-items: center; justify-content: space-between;"
      >
        <n-breadcrumb>
          <n-breadcrumb-item>Ana Sayfa</n-breadcrumb-item>
          <n-breadcrumb-item>{{ route.meta.title }}</n-breadcrumb-item>
        </n-breadcrumb>

        <n-space align="center">
          <n-tag type="success" size="small">v1.0.0</n-tag>
          <n-dropdown
            :options="userDropdownOptions"
            @select="handleUserAction"
            trigger="click"
          >
            <n-space align="center" style="cursor: pointer">
              <n-avatar round size="small" style="background: #1890ff">
                {{ authStore.fullName?.[0]?.toUpperCase() || 'U' }}
              </n-avatar>
              <n-text>{{ authStore.fullName }}</n-text>
              <n-icon :component="ChevronDownOutline" size="14" />
            </n-space>
          </n-dropdown>
        </n-space>
      </n-layout-header>

      <!-- Page Content -->
      <n-layout-content
        content-style="padding: 24px; background: #f0f2f5; min-height: calc(100vh - 64px)"
      >
        <RouterView />
      </n-layout-content>
    </n-layout>
  </n-layout>
</template>

<style scoped>
.sidebar-logo {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px 18px;
  border-bottom: 1px solid rgba(255,255,255,0.1);
  overflow: hidden;
  white-space: nowrap;
}

.sidebar-logo.collapsed {
  justify-content: center;
  padding: 20px 0;
}

.logo-icon {
  font-size: 24px;
  flex-shrink: 0;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>