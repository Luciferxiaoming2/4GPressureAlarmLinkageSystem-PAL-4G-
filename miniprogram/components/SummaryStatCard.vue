<template>
  <view class="summary-card" :class="accentClass">
    <text class="summary-card__label">{{ label }}</text>
    <text class="summary-card__value">{{ value }}</text>
    <text v-if="hint" class="summary-card__hint">{{ hint }}</text>
  </view>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  label: {
    type: String,
    required: true,
  },
  value: {
    type: [String, Number],
    default: '--',
  },
  hint: {
    type: String,
    default: '',
  },
  accent: {
    type: String,
    default: 'blue',
  },
})

const accentClass = computed(() => `summary-card--${props.accent}`)
</script>

<style scoped>
.summary-card {
  min-height: 166rpx;
  padding: 26rpx 24rpx;
  border-radius: 26rpx;
  color: #17324d;
}

.summary-card--blue {
  background: linear-gradient(160deg, rgba(22, 93, 255, 0.14), rgba(44, 159, 255, 0.06));
}

.summary-card--green {
  background: linear-gradient(160deg, rgba(17, 181, 110, 0.16), rgba(17, 181, 110, 0.05));
}

.summary-card--orange {
  background: linear-gradient(160deg, rgba(255, 164, 38, 0.18), rgba(255, 164, 38, 0.05));
}

.summary-card--red {
  background: linear-gradient(160deg, rgba(231, 77, 60, 0.18), rgba(231, 77, 60, 0.05));
}

.summary-card__label {
  display: block;
  font-size: 24rpx;
  line-height: 1.5;
  color: #5f7896;
}

.summary-card__value {
  display: block;
  margin-top: 14rpx;
  font-size: 46rpx;
  font-weight: 700;
  line-height: 1.15;
}

.summary-card__hint {
  display: block;
  margin-top: 12rpx;
  font-size: 22rpx;
  line-height: 1.6;
  color: #7088a4;
}
</style>
