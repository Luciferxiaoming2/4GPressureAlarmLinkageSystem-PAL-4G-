<template>
  <view class="app-page app-page--docked">
    <view class="hero-panel">
      <text class="alarms-hero__eyebrow">报警中心</text>
      <text class="alarms-hero__title">历史报警</text>
      <text class="alarms-hero__desc">报警筛选和分页查询单独放在这里，首页只做最近预览。</text>
    </view>

    <SectionCard title="筛选条件" subtitle="先筛后查，避免在首页塞太多过滤项。">
      <view class="form-field">
        <text class="form-label">关键词</text>
        <input v-model.trim="filters.keyword" class="form-input" placeholder="设备名称或 SN" />
      </view>

      <view class="form-field">
        <text class="form-label">报警类型</text>
        <view class="filter-chip-list">
          <view
            v-for="item in alarmTypeOptions"
            :key="item.value || 'all'"
            class="filter-chip"
            :class="filters.alarmType === item.value ? 'filter-chip--active' : ''"
            @click="filters.alarmType = item.value"
          >
            {{ item.label }}
          </view>
        </view>
      </view>

      <view class="date-grid">
        <view class="form-field">
          <text class="form-label">开始日期</text>
          <picker mode="date" :value="filters.triggeredFrom" @change="filters.triggeredFrom = $event.detail.value">
            <view class="form-input picker-input">{{ filters.triggeredFrom || '请选择开始日期' }}</view>
          </picker>
        </view>
        <view class="form-field">
          <text class="form-label">结束日期</text>
          <picker mode="date" :value="filters.triggeredTo" @change="filters.triggeredTo = $event.detail.value">
            <view class="form-input picker-input">{{ filters.triggeredTo || '请选择结束日期' }}</view>
          </picker>
        </view>
      </view>

      <view class="filter-actions">
        <button class="secondary-button" @click="handleReset">重置筛选</button>
        <button class="primary-button" @click="handleSearch">立即查询</button>
      </view>
    </SectionCard>

    <view v-if="loading && !items.length" class="panel-card">
      <text class="text-muted">正在加载报警记录...</text>
    </view>

    <SectionCard v-else title="报警列表" :subtitle="listSubtitle">
      <template v-if="items.length">
        <view class="alarm-list">
          <view v-for="item in items" :key="item.id" class="panel-card alarm-record">
            <view class="alarm-record__head">
              <view>
                <text class="alarm-record__title">{{ item.device_name }}</text>
                <text class="alarm-record__time">{{ formatDateTime(item.triggered_at) }}</text>
              </view>
              <text class="status-tag status-alarm">{{ getAlarmTypeLabel(item.alarm_type) }}</text>
            </view>

            <view class="alarm-record__meta">
              <text class="alarm-record__meta-item">状态：{{ item.alarm_status || '--' }}</text>
              <text class="alarm-record__meta-item">联动：{{ item.linkage_status || '--' }}</text>
              <text class="alarm-record__meta-item">来源：{{ item.source || '--' }}</text>
            </view>

            <text class="alarm-record__message">{{ item.message || '该报警没有额外说明。' }}</text>
          </view>
        </view>

        <button v-if="hasMore" class="secondary-button load-more" :loading="loadingMore" @click="loadMore">
          加载更多
        </button>
      </template>

      <EmptyState
        v-else
        title="暂无报警记录"
        description="你可以先放宽筛选条件，或等待设备上报新的报警信息。"
        action-text="重新查询"
        @action="handleSearch"
      />
    </SectionCard>

    <PrimaryDock active="alarms" />
  </view>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { onPullDownRefresh, onReachBottom, onShow } from '@dcloudio/uni-app'

import EmptyState from '@/components/EmptyState.vue'
import PrimaryDock from '@/components/PrimaryDock.vue'
import SectionCard from '@/components/SectionCard.vue'
import { getAlarmPageApi } from '@/api/dashboard'
import { showRequestError } from '@/utils/errors'
import { formatDateTime } from '@/utils/format'
import { ensureAuthenticated } from '@/utils/guards'
import { getAlarmTypeLabel } from '@/utils/status'

const DEFAULT_LIMIT = 10
const items = ref([])
const total = ref(0)
const loading = ref(false)
const loadingMore = ref(false)

const filters = reactive({
  keyword: '',
  alarmType: '',
  triggeredFrom: '',
  triggeredTo: '',
})

const alarmTypeOptions = [
  { label: '全部', value: '' },
  { label: '低电量', value: 'low_battery' },
  { label: '低压', value: 'low_voltage' },
  { label: '高压', value: 'high_voltage' },
  { label: '离线', value: 'disconnect' },
]

const hasMore = computed(() => items.value.length < total.value)

const listSubtitle = computed(() => {
  if (total.value) {
    return `当前查询到 ${total.value} 条报警记录。`
  }
  return '按时间和报警类型快速排查历史事件。'
})

function buildParams(offset) {
  return {
    limit: DEFAULT_LIMIT,
    offset,
    keyword: filters.keyword || undefined,
    alarm_type: filters.alarmType || undefined,
    triggered_from: filters.triggeredFrom ? `${filters.triggeredFrom}T00:00:00` : undefined,
    triggered_to: filters.triggeredTo ? `${filters.triggeredTo}T23:59:59` : undefined,
  }
}

async function loadAlarms({ reset = false } = {}) {
  if (!(await ensureAuthenticated())) {
    return
  }

  const nextOffset = reset ? 0 : items.value.length
  if (reset) {
    loading.value = true
  } else {
    loadingMore.value = true
  }

  try {
    const page = await getAlarmPageApi(buildParams(nextOffset))
    total.value = page.pagination.total
    items.value = reset ? page.items : items.value.concat(page.items)
  } catch (error) {
    showRequestError(error, '报警记录加载失败')
  } finally {
    loading.value = false
    loadingMore.value = false
    uni.stopPullDownRefresh()
  }
}

function handleSearch() {
  void loadAlarms({ reset: true })
}

function handleReset() {
  filters.keyword = ''
  filters.alarmType = ''
  filters.triggeredFrom = ''
  filters.triggeredTo = ''
  void loadAlarms({ reset: true })
}

function loadMore() {
  if (!hasMore.value || loadingMore.value) {
    return
  }
  void loadAlarms({ reset: false })
}

onShow(() => {
  if (!items.value.length) {
    void loadAlarms({ reset: true })
  }
})

onPullDownRefresh(() => {
  void loadAlarms({ reset: true })
})

onReachBottom(() => {
  loadMore()
})
</script>

<style scoped>
.alarms-hero__eyebrow,
.alarms-hero__desc,
.alarm-record__title,
.alarm-record__time,
.alarm-record__message {
  display: block;
}

.alarms-hero__eyebrow {
  font-size: 24rpx;
  letter-spacing: 3rpx;
  opacity: 0.84;
}

.alarms-hero__title {
  display: block;
  margin-top: 12rpx;
  font-size: 42rpx;
  font-weight: 700;
}

.alarms-hero__desc {
  margin-top: 18rpx;
  font-size: 24rpx;
  line-height: 1.7;
  opacity: 0.92;
}

.filter-chip-list {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
}

.filter-chip {
  padding: 14rpx 22rpx;
  border-radius: 999rpx;
  background: rgba(20, 87, 151, 0.06);
  font-size: 24rpx;
  color: #5f7a9a;
}

.filter-chip--active {
  background: rgba(22, 93, 255, 0.14);
  color: #165dff;
  font-weight: 700;
}

.date-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 16rpx;
}

.picker-input {
  display: flex;
  align-items: center;
}

.filter-actions {
  display: grid;
  gap: 16rpx;
}

.filter-actions button {
  width: 100%;
}

.alarm-list {
  display: grid;
  gap: 18rpx;
}

.alarm-record {
  padding: 28rpx;
}

.alarm-record__head {
  display: flex;
  flex-direction: column;
  gap: 18rpx;
}

.alarm-record__title {
  font-size: 28rpx;
  font-weight: 700;
  line-height: 1.5;
}

.alarm-record__time {
  margin-top: 8rpx;
  font-size: 22rpx;
  color: #879db3;
}

.alarm-record__meta {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx 20rpx;
  margin-top: 18rpx;
}

.alarm-record__meta-item {
  font-size: 22rpx;
  color: #5f7895;
}

.alarm-record__message {
  margin-top: 14rpx;
  font-size: 24rpx;
  line-height: 1.7;
  color: #6f85a1;
}

.load-more {
  margin-top: 24rpx;
}
</style>
