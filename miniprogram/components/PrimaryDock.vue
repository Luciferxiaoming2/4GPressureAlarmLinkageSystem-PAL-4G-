<template>
  <view class="primary-dock">
    <view class="primary-dock__shell">
      <view
        v-for="item in items"
        :key="item.key"
        class="primary-dock__item"
        :class="active === item.key ? 'primary-dock__item--active' : ''"
        @click="handleNavigate(item)"
      >
        <view class="primary-dock__icon">
          <view v-if="item.key === 'home'" class="dock-home">
            <view class="dock-home__roof" />
            <view class="dock-home__body" />
          </view>

          <view v-else-if="item.key === 'devices'" class="dock-grid">
            <view class="dock-grid__cell" />
            <view class="dock-grid__cell" />
            <view class="dock-grid__cell" />
            <view class="dock-grid__cell" />
          </view>

          <view v-else-if="item.key === 'alarms'" class="dock-bell">
            <view class="dock-bell__body" />
            <view class="dock-bell__dot" />
          </view>

          <view v-else class="dock-user">
            <view class="dock-user__head" />
            <view class="dock-user__body" />
          </view>
        </view>

        <text class="primary-dock__label">{{ item.label }}</text>
      </view>
    </view>
  </view>
</template>

<script setup>
const props = defineProps({
  active: {
    type: String,
    required: true,
  },
})

const items = [
  {
    key: 'home',
    label: '首页',
    url: '/pages/home/index',
  },
  {
    key: 'devices',
    label: '设备',
    url: '/pages/devices/index',
  },
  {
    key: 'alarms',
    label: '报警',
    url: '/pages/alarms/index',
  },
  {
    key: 'profile',
    label: '我的',
    url: '/pages/profile/index',
  },
]

function handleNavigate(item) {
  if (props.active === item.key) {
    return
  }

  uni.reLaunch({
    url: item.url,
  })
}
</script>

<style scoped>
.primary-dock {
  position: fixed;
  left: 24rpx;
  right: 24rpx;
  bottom: calc(20rpx + env(safe-area-inset-bottom));
  z-index: 30;
}

.primary-dock__shell {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10rpx;
  padding: 12rpx;
  border: 1rpx solid rgba(24, 71, 132, 0.08);
  border-radius: 32rpx;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 20rpx 42rpx rgba(26, 69, 122, 0.14);
}

.primary-dock__item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10rpx;
  padding: 14rpx 8rpx 12rpx;
  border-radius: 24rpx;
  transition: all 0.2s ease;
}

.primary-dock__item--active {
  background: rgba(22, 93, 255, 0.1);
}

.primary-dock__icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 56rpx;
  height: 56rpx;
  border-radius: 18rpx;
  background: rgba(22, 93, 255, 0.07);
}

.primary-dock__item--active .primary-dock__icon {
  background: rgba(22, 93, 255, 0.16);
}

.primary-dock__label {
  font-size: 20rpx;
  font-weight: 600;
  color: #7991ab;
}

.primary-dock__item--active .primary-dock__label {
  color: #165dff;
}

.dock-home,
.dock-grid,
.dock-bell,
.dock-user {
  position: relative;
}

.dock-home {
  width: 30rpx;
  height: 28rpx;
}

.dock-home__roof {
  width: 0;
  height: 0;
  margin: 0 auto;
  border-left: 12rpx solid transparent;
  border-right: 12rpx solid transparent;
  border-bottom: 12rpx solid #6f87a4;
}

.dock-home__body {
  width: 20rpx;
  height: 14rpx;
  margin: 2rpx auto 0;
  border-radius: 6rpx;
  background: #6f87a4;
}

.primary-dock__item--active .dock-home__roof,
.primary-dock__item--active .dock-home__body,
.primary-dock__item--active .dock-grid__cell,
.primary-dock__item--active .dock-bell__body,
.primary-dock__item--active .dock-bell__dot,
.primary-dock__item--active .dock-user__head,
.primary-dock__item--active .dock-user__body {
  background: #165dff;
  border-bottom-color: #165dff;
}

.dock-grid {
  display: grid;
  grid-template-columns: repeat(2, 10rpx);
  gap: 4rpx;
}

.dock-grid__cell {
  width: 10rpx;
  height: 10rpx;
  border-radius: 4rpx;
  background: #6f87a4;
}

.dock-bell {
  width: 26rpx;
  height: 28rpx;
}

.dock-bell__body {
  width: 22rpx;
  height: 18rpx;
  margin: 0 auto;
  border-radius: 12rpx 12rpx 8rpx 8rpx;
  background: #6f87a4;
}

.dock-bell__dot {
  width: 8rpx;
  height: 8rpx;
  margin: 2rpx auto 0;
  border-radius: 999rpx;
  background: #6f87a4;
}

.dock-user {
  width: 26rpx;
  height: 28rpx;
}

.dock-user__head {
  width: 12rpx;
  height: 12rpx;
  margin: 0 auto;
  border-radius: 999rpx;
  background: #6f87a4;
}

.dock-user__body {
  width: 20rpx;
  height: 10rpx;
  margin: 4rpx auto 0;
  border-radius: 10rpx 10rpx 8rpx 8rpx;
  background: #6f87a4;
}
</style>
