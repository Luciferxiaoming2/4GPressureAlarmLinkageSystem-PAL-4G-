<template>
  <view class="app-page">
    <view class="hero-panel">
      <text class="settings-title">设置</text>
      <text class="settings-desc">消息订阅、修改密码和退出登录统一放在这里处理，避免“我的”页承载过多操作。</text>
    </view>

    <SectionCard title="报警消息订阅" subtitle="消息授权已收纳到设置页，统一管理提醒能力。">
      <view class="settings-info__row settings-info__row--compact">
        <text class="settings-info__label">授权状态</text>
        <text class="settings-info__value">{{ subscriptionStore.state.enabled ? '已授权' : '未授权' }}</text>
      </view>
      <view class="settings-info__row settings-info__row--compact">
        <text class="settings-info__label">最近更新时间</text>
        <text class="settings-info__value">{{ formatDateTime(subscriptionStore.state.updatedAt, '尚未授权') }}</text>
      </view>
      <button class="secondary-button settings-action" @click="handleSubscribe">申请授权</button>
    </SectionCard>

    <SectionCard title="修改密码" subtitle="修改成功后将自动退出并要求重新登录。">
      <view class="form-field">
        <text class="form-label">当前密码</text>
        <input v-model="passwordForm.currentPassword" class="form-input" password placeholder="请输入当前密码" />
      </view>
      <view class="form-field">
        <text class="form-label">新密码</text>
        <input v-model="passwordForm.newPassword" class="form-input" password placeholder="请输入新密码" />
      </view>
      <view class="form-field">
        <text class="form-label">确认新密码</text>
        <input v-model="passwordForm.confirmPassword" class="form-input" password placeholder="请再次输入新密码" />
      </view>
      <button class="primary-button settings-action" :loading="submittingPassword" @click="handleChangePassword">
        确认修改密码
      </button>
    </SectionCard>

    <SectionCard title="退出登录" subtitle="退出后需要重新输入账号密码登录。">
      <button class="danger-button settings-action" @click="handleLogout">安全退出</button>
    </SectionCard>
  </view>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'

import SectionCard from '@/components/SectionCard.vue'
import { changePasswordApi } from '@/api/users'
import { useAuthStore } from '@/stores/auth'
import { showRequestError } from '@/utils/errors'
import { formatDateTime } from '@/utils/format'
import { ensureAuthenticated } from '@/utils/guards'
import { useSubscriptionStore } from '@/utils/subscription'

const authStore = useAuthStore()
const subscriptionStore = useSubscriptionStore()

const submittingPassword = ref(false)
const passwordForm = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: '',
})

onShow(() => {
  void ensureAuthenticated()
})

async function handleSubscribe() {
  try {
    const granted = await subscriptionStore.requestAlarmSubscription()
    uni.showToast({
      title: granted ? '授权成功' : '你已拒绝授权',
      icon: 'none',
    })
  } catch (error) {
    showRequestError(error, '订阅能力待后端联调')
  }
}

async function handleChangePassword() {
  if (!(await ensureAuthenticated())) {
    return
  }

  if (!passwordForm.currentPassword || !passwordForm.newPassword || !passwordForm.confirmPassword) {
    uni.showToast({
      title: '请完整填写密码信息',
      icon: 'none',
    })
    return
  }

  if (passwordForm.newPassword.length < 8) {
    uni.showToast({
      title: '新密码至少 8 位',
      icon: 'none',
    })
    return
  }

  if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    uni.showToast({
      title: '两次输入的新密码不一致',
      icon: 'none',
    })
    return
  }

  submittingPassword.value = true
  try {
    await changePasswordApi({
      current_password: passwordForm.currentPassword,
      new_password: passwordForm.newPassword,
    })
    uni.showToast({
      title: '密码已更新，请重新登录',
      icon: 'none',
    })
    authStore.logout(false)
    uni.reLaunch({
      url: '/pages/login/index',
    })
  } catch (error) {
    showRequestError(error, '修改密码失败')
  } finally {
    submittingPassword.value = false
  }
}

function handleLogout() {
  authStore.logout(false)
  uni.reLaunch({
    url: '/pages/login/index',
  })
}
</script>

<style scoped>
.settings-title {
  display: block;
  font-size: 42rpx;
  font-weight: 700;
}

.settings-desc {
  display: block;
  margin-top: 18rpx;
  font-size: 24rpx;
  line-height: 1.7;
  opacity: 0.92;
}

.settings-action {
  margin-top: 12rpx;
}

.settings-info__row {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 20rpx;
  padding: 18rpx 0;
  border-top: 1rpx solid rgba(22, 83, 143, 0.08);
}

.settings-info__row:first-child {
  padding-top: 0;
  border-top: 0;
}

.settings-info__row--compact {
  gap: 12rpx;
}

.settings-info__label {
  font-size: 24rpx;
  color: #6f87a4;
}

.settings-info__value {
  font-size: 24rpx;
  line-height: 1.5;
  color: #17324d;
  font-weight: 600;
}
</style>
