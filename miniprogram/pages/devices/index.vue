<template>
  <view class="app-page app-page--docked">
    <view class="hero-panel">
      <text class="devices-hero__eyebrow">设备中心</text>
      <text class="devices-hero__title">我的设备</text>
      <text class="devices-hero__desc">这里单独负责设备查看、搜索和进入详情，不再混在首页长列表里。</text>
      <view class="devices-hero__meta">
        <view class="devices-hero__meta-card">
          <text class="devices-hero__meta-label">设备数</text>
          <text class="devices-hero__meta-value">{{ devices.length }}</text>
        </view>
        <view class="devices-hero__meta-card">
          <text class="devices-hero__meta-label">在线设备</text>
          <text class="devices-hero__meta-value">{{ onlineDeviceCount }}</text>
        </view>
      </view>
    </view>

    <SectionCard title="设备工具" subtitle="搜索、刷新和绑定设备都放在这个区域，操作边界更清晰。">
      <input v-model.trim="keyword" class="form-input" placeholder="搜索设备名称或 SN" />
      <view class="tool-actions">
        <button class="secondary-button" @click="refreshDevices">刷新列表</button>
        <button class="primary-button" @click="openBindPage">绑定设备</button>
      </view>
    </SectionCard>

    <view v-if="loading" class="panel-card">
      <text class="text-muted">正在同步设备列表...</text>
    </view>

    <SectionCard v-else title="设备列表" :subtitle="listSubtitle">
      <template v-if="filteredDevices.length">
        <view class="device-list">
          <DeviceSummaryCard
            v-for="item in filteredDevices"
            :key="item.device_id"
            :device="item"
            @open="openDeviceDetail"
          />
        </view>
      </template>
      <EmptyState
        v-else
        title="暂无可见设备"
        description="你可以通过输入序列号绑定设备，绑定后会立即进入移动端管理范围。"
        action-text="立即绑定"
        @action="openBindPage"
      />
    </SectionCard>

    <PrimaryDock active="devices" />
  </view>
</template>

<script setup>
import { computed, onUnmounted, ref } from 'vue'
import { onPullDownRefresh, onShow } from '@dcloudio/uni-app'

import DeviceSummaryCard from '@/components/DeviceSummaryCard.vue'
import EmptyState from '@/components/EmptyState.vue'
import PrimaryDock from '@/components/PrimaryDock.vue'
import SectionCard from '@/components/SectionCard.vue'
import { getMyDevicesApi } from '@/api/dashboard'
import { useRealtime } from '@/composables/useRealtime'
import { showRequestError } from '@/utils/errors'
import { ensureAuthenticated } from '@/utils/guards'

const realtime = useRealtime()

const loading = ref(false)
const keyword = ref('')
const devices = ref([])
let stopRealtime = null

const filteredDevices = computed(() => {
  const search = keyword.value.trim().toLowerCase()
  if (!search) {
    return devices.value
  }

  return devices.value.filter((item) => {
    return (
      String(item.device_name || '').toLowerCase().includes(search) ||
      String(item.serial_number || '').toLowerCase().includes(search)
    )
  })
})

const onlineDeviceCount = computed(() =>
  devices.value.filter((item) => {
    return item.device_status === 'active' || Number(item.online_module_count || 0) > 0
  }).length,
)

const listSubtitle = computed(() => {
  if (keyword.value.trim()) {
    return `共匹配到 ${filteredDevices.value.length} 台设备。`
  }

  return `当前账号下共有 ${devices.value.length} 台设备。`
})

async function loadDevices(showLoading = true) {
  if (!(await ensureAuthenticated())) {
    return
  }

  if (showLoading) {
    loading.value = true
  }

  try {
    devices.value = await getMyDevicesApi()
  } catch (error) {
    showRequestError(error, '设备列表加载失败')
  } finally {
    loading.value = false
    uni.stopPullDownRefresh()
  }
}

function refreshDevices() {
  void loadDevices()
}

function openDeviceDetail(deviceId) {
  uni.navigateTo({
    url: `/pages/device-detail/index?deviceId=${deviceId}`,
  })
}

function openBindPage() {
  uni.navigateTo({
    url: '/pages/device-bind/index',
  })
}

onShow(() => {
  void loadDevices()
  if (!stopRealtime) {
    stopRealtime = realtime.subscribe((message) => {
      if (
        ['alarm.created', 'alarm.recovered', 'module.status_updated', 'relay_command.created', 'relay_command.updated'].includes(
          message?.event,
        )
      ) {
        void loadDevices(false)
      }
    })
  }
})

onPullDownRefresh(() => {
  void loadDevices(false)
})

onUnmounted(() => {
  if (stopRealtime) {
    stopRealtime()
    stopRealtime = null
  }
})
</script>

<style scoped>
.devices-hero__eyebrow,
.devices-hero__desc,
.devices-hero__meta-label,
.devices-hero__meta-value {
  display: block;
}

.devices-hero__eyebrow {
  font-size: 24rpx;
  letter-spacing: 3rpx;
  opacity: 0.84;
}

.devices-hero__title {
  display: block;
  margin-top: 12rpx;
  font-size: 42rpx;
  font-weight: 700;
}

.devices-hero__desc {
  margin-top: 18rpx;
  font-size: 24rpx;
  line-height: 1.7;
  opacity: 0.92;
}

.devices-hero__meta {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18rpx;
  margin-top: 24rpx;
}

.devices-hero__meta-card {
  padding: 18rpx;
  border-radius: 22rpx;
  background: rgba(255, 255, 255, 0.14);
}

.devices-hero__meta-label {
  font-size: 22rpx;
  opacity: 0.88;
}

.devices-hero__meta-value {
  margin-top: 10rpx;
  font-size: 36rpx;
  font-weight: 700;
}

.tool-actions {
  display: grid;
  gap: 16rpx;
  margin-top: 18rpx;
}

.device-list {
  display: grid;
  gap: 18rpx;
}
</style>
