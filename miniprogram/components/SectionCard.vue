<template>
  <view class="panel-card section-card">
    <view class="section-card__head">
      <view>
        <text class="section-card__title">{{ title }}</text>
        <text v-if="subtitle" class="section-card__subtitle">{{ subtitle }}</text>
      </view>
      <slot name="extra" />
    </view>
    <slot />
  </view>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    required: true,
  },
  subtitle: {
    type: String,
    default: '',
  },
})
</script>

<style scoped>
.section-card__head {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 16rpx;
  margin-bottom: 24rpx;
}

.section-card__title {
  display: block;
  font-size: 30rpx;
  font-weight: 700;
  color: #17324d;
}

.section-card__subtitle {
  display: block;
  margin-top: 8rpx;
  font-size: 22rpx;
  line-height: 1.6;
  color: #7087a3;
}
</style>
