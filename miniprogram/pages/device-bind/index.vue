<template>
  <view class="app-page">
    <view class="hero-panel">
      <text class="section-title">绑定新设备</text>
      <text class="section-subtitle">
        输入设备序列号即可将新设备纳入当前账号的监控和控制范围。
      </text>
    </view>

    <view class="panel-card bind-form">
      <view class="form-field">
        <text class="form-label">设备序列号 SN</text>
        <input v-model.trim="form.serialNumber" class="form-input" placeholder="请输入设备序列号" />
      </view>

      <view class="form-field">
        <text class="form-label">设备显示名称（可选）</text>
        <input v-model.trim="form.name" class="form-input" placeholder="例如：泵房 A 组" />
      </view>

      <view class="bind-actions">
        <button class="secondary-button" @click="handleScan">扫码填充</button>
        <button class="primary-button" :loading="submitting" @click="handleSubmit">确认绑定</button>
      </view>
    </view>
  </view>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'

import { bindDeviceApi } from '@/api/devices'
import { showRequestError } from '@/utils/errors'
import { ensureAuthenticated } from '@/utils/guards'

const form = reactive({
  serialNumber: '',
  name: '',
})
const submitting = ref(false)

onShow(() => {
  void ensureAuthenticated()
})

function handleScan() {
  uni.scanCode({
    onlyFromCamera: false,
    success: (result) => {
      form.serialNumber = result.result || ''
    },
    fail: () => {
      uni.showToast({
        title: '扫码未完成',
        icon: 'none',
      })
    },
  })
}

async function handleSubmit() {
  if (!(await ensureAuthenticated())) {
    return
  }

  if (!form.serialNumber) {
    uni.showToast({
      title: '请输入设备序列号',
      icon: 'none',
    })
    return
  }

  submitting.value = true
  try {
    const device = await bindDeviceApi({
      serial_number: form.serialNumber,
      name: form.name || undefined,
    })
    uni.showToast({
      title: '绑定成功',
      icon: 'success',
    })
    uni.redirectTo({
      url: `/pages/device-detail/index?deviceId=${device.id}`,
    })
  } catch (error) {
    showRequestError(error, '设备绑定失败')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.bind-actions {
  display: grid;
  gap: 16rpx;
  margin-top: 10rpx;
}

.bind-actions button {
  width: 100%;
}
</style>
