<template>
  <view class="panel-card empty-state">
    <text class="empty-title">{{ title }}</text>
    <text class="empty-description">{{ description }}</text>
    <button v-if="actionText" class="secondary-button empty-action" @click="$emit('action')">
      {{ actionText }}
    </button>
  </view>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    default: '暂无数据',
  },
  description: {
    type: String,
    default: '当前还没有可展示的内容。',
  },
  actionText: {
    type: String,
    default: '',
  },
})

defineEmits(['action'])
</script>

<style scoped>
.empty-state {
  align-items: center;
  text-align: center;
}

.empty-title {
  font-size: 30rpx;
  font-weight: 700;
  color: #1a3656;
}

.empty-description {
  margin-top: 12rpx;
  font-size: 24rpx;
  line-height: 1.6;
  color: #6e84a2;
}

.empty-action {
  margin-top: 24rpx;
}
</style>
