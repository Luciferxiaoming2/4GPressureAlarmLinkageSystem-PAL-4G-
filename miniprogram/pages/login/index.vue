<template>
  <view class="app-page login-page">
    <view class="hero-panel login-hero">
      <text class="login-hero__eyebrow">PAL_4G 移动控制台</text>
      <text class="login-hero__title">4G 压力报警联动系统</text>
      <text class="login-hero__desc">
        使用设备账号直接登录，快速查看设备状态、接收报警并进行远程控制。
      </text>
    </view>

    <view class="panel-card login-form">
      <view class="form-field">
        <text class="form-label">账号</text>
        <input
          v-model.trim="form.username"
          class="form-input"
          placeholder="请输入账号"
          confirm-type="next"
        />
      </view>

      <view class="form-field">
        <text class="form-label">密码</text>
        <input
          v-model="form.password"
          class="form-input"
          password
          placeholder="请输入密码"
          confirm-type="done"
          @confirm="handleLogin"
        />
      </view>

      <button class="primary-button login-submit" :loading="authStore.state.loading" @click="handleLogin">
        登录并进入控制中心
      </button>

      <button class="secondary-button login-wechat" @click="handleWechatLogin">
        微信授权登录（待联调）
      </button>

      <view class="login-tips">
        <text class="login-tips__title">当前版本说明</text>
        <text class="login-tips__item">1. 账号密码登录已可直接联调后端。</text>
        <text class="login-tips__item">2. 微信授权登录与账号绑定入口已预留，等待后端接入。</text>
        <text class="login-tips__item">3. 默认接口地址可在 `miniprogram/utils/config.js` 中调整。</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { reactive } from 'vue'
import { onShow } from '@dcloudio/uni-app'

import { useAuthStore } from '@/stores/auth'
import { APP_CONFIG } from '@/utils/config'
import { showRequestError } from '@/utils/errors'

const authStore = useAuthStore()
const form = reactive({
  username: '',
  password: '',
})

async function redirectIfLoggedIn() {
  await authStore.initialize()
  if (authStore.isAuthenticated.value) {
    uni.reLaunch({
      url: '/pages/home/index',
    })
  }
}

async function handleLogin() {
  if (!form.username || !form.password) {
    uni.showToast({
      title: '请输入账号和密码',
      icon: 'none',
    })
    return
  }

  try {
    await authStore.login(form.username, form.password)
    uni.showToast({
      title: '登录成功',
      icon: 'success',
    })
    uni.reLaunch({
      url: '/pages/home/index',
    })
  } catch (error) {
    showRequestError(error, '登录失败，请检查账号密码')
  }
}

function handleWechatLogin() {
  uni.showModal({
    title: '微信授权待联调',
    content: APP_CONFIG.WECHAT_LOGIN_ENABLED
      ? '后端微信登录接口尚未接入完成，请先使用账号密码登录。'
      : '当前项目已预留微信授权入口，但默认未启用，请在后端完成接口与配置后再开启。',
    showCancel: false,
  })
}

onShow(() => {
  void redirectIfLoggedIn()
})
</script>

<style scoped>
.login-page {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 28rpx;
  padding-top: 64rpx;
}

.login-hero__eyebrow {
  display: block;
  font-size: 24rpx;
  letter-spacing: 3rpx;
  opacity: 0.82;
}

.login-hero__title {
  display: block;
  margin-top: 14rpx;
  font-size: 46rpx;
  font-weight: 700;
  line-height: 1.3;
}

.login-hero__desc {
  display: block;
  margin-top: 18rpx;
  font-size: 24rpx;
  line-height: 1.7;
  opacity: 0.92;
}

.login-submit {
  margin-top: 8rpx;
}

.login-wechat {
  margin-top: 18rpx;
}

.login-tips {
  margin-top: 26rpx;
  padding: 24rpx;
  border-radius: 22rpx;
  background: rgba(17, 77, 141, 0.05);
}

.login-tips__title {
  display: block;
  font-size: 24rpx;
  font-weight: 700;
  color: #1e4065;
}

.login-tips__item {
  display: block;
  margin-top: 12rpx;
  font-size: 22rpx;
  line-height: 1.6;
  color: #69809b;
}
</style>
