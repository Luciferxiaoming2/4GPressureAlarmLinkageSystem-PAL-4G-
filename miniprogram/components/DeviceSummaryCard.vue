<template>
  <view class="panel-card device-card" @click="$emit('open', device.device_id)">
    <view class="device-card__head">
      <view>
        <text class="device-card__title">{{ device.device_name }}</text>
        <text class="device-card__serial">SN：{{ device.serial_number || '--' }}</text>
      </view>
      <text class="status-tag" :class="device.device_status === 'active' ? 'status-online' : 'status-offline'">
        {{ device.device_status === 'active' ? '运行中' : '停用' }}
      </text>
    </view>

    <view class="device-card__grid">
      <view class="device-card__metric">
        <text class="device-card__metric-label">在线状态</text>
        <text class="device-card__metric-value device-card__metric-value--small">
          {{ onlineStatusText }}
        </text>
      </view>
      <view class="device-card__metric">
        <text class="device-card__metric-label">最近报警</text>
        <text class="device-card__metric-value device-card__metric-value--small">
          {{ alarmLabel }}
        </text>
      </view>
      <view class="device-card__metric">
        <text class="device-card__metric-label">报警时间</text>
        <text class="device-card__metric-value device-card__metric-value--small">
          {{ latestAlarmTime }}
        </text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { computed } from 'vue'

import { formatDateTime } from '@/utils/format'
import { getAlarmTypeLabel } from '@/utils/status'

const props = defineProps({
  device: {
    type: Object,
    required: true,
  },
})

defineEmits(['open'])

const alarmLabel = computed(() => getAlarmTypeLabel(props.device.latest_alarm_type))
const latestAlarmTime = computed(() => formatDateTime(props.device.latest_alarm_time))
const onlineStatusText = computed(() =>
  Number(props.device.online_module_count || 0) > 0 ? '在线' : '离线',
)
</script>

<style scoped>
.device-card__head {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.device-card__title {
  display: block;
  font-size: 30rpx;
  font-weight: 700;
  line-height: 1.4;
}

.device-card__serial {
  display: block;
  margin-top: 10rpx;
  font-size: 22rpx;
  line-height: 1.6;
  color: #6e84a2;
}

.device-card__grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 14rpx;
  margin-top: 24rpx;
}

.device-card__metric {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18rpx;
  padding: 20rpx 22rpx;
  border-radius: 22rpx;
  background: rgba(18, 89, 164, 0.05);
}

.device-card__metric-label {
  flex: 0 0 auto;
  font-size: 22rpx;
  line-height: 1.5;
  color: #68809d;
}

.device-card__metric-value {
  flex: 1;
  min-width: 0;
  text-align: right;
  font-size: 32rpx;
  font-weight: 700;
  line-height: 1.35;
}

.device-card__metric-value--small {
  font-size: 24rpx;
  line-height: 1.5;
}
</style>
