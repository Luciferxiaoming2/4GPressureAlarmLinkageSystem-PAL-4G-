<template>
  <article class="module-card">
    <header class="module-card__head">
      <div class="module-card__identity">
        <p>{{ item.device_name }}</p>
        <strong>设备状态</strong>
        <span>{{ item.serial_number }}</span>
      </div>
      <StatusPill :value="item.is_online ? 'online' : 'offline'" :mapping="onlineStatusMeta" />
    </header>

    <div class="module-card__grid">
      <div class="module-card__metric">
        <span>{{ t('dashboard.modulePanels.battery') }}</span>
        <strong>{{ formatBattery(item.battery_level) }}</strong>
      </div>
      <div class="module-card__metric">
        <span>{{ t('dashboard.modulePanels.voltage') }}</span>
        <strong>{{ formatVoltage(item.voltage_value) }}</strong>
      </div>
      <div class="module-card__metric">
        <span>{{ t('dashboard.modulePanels.relay') }}</span>
        <strong>{{ item.relay_state ? t('status.relay.closed') : t('status.relay.open') }}</strong>
      </div>
      <div class="module-card__metric">
        <span>{{ t('dashboard.modulePanels.lastSeen') }}</span>
        <strong>{{ formatDateTime(item.last_seen_at) }}</strong>
      </div>
      <div class="module-card__metric">
        <span>{{ t('dashboard.modulePanels.latestAlarmType') }}</span>
        <strong>{{ resolveAlarmType(item.latest_alarm_type) }}</strong>
      </div>
      <div class="module-card__metric">
        <span>{{ t('dashboard.modulePanels.latestAlarmTime') }}</span>
        <strong>{{ formatDateTime(item.latest_alarm_time) }}</strong>
      </div>
    </div>
  </article>
</template>

<script setup lang="ts">
import StatusPill from '@/components/StatusPill.vue'
import { useI18n } from '@/composables/useI18n'
import type { DashboardModulePanelItem } from '@/types/domain'
import { formatBattery, formatDateTime, formatVoltage } from '@/utils/format'

defineProps<{
  item: DashboardModulePanelItem
}>()

const { t } = useI18n()

const onlineStatusMeta = {
  online: { type: 'success', labelKey: 'dashboard.modulePanels.status.online' },
  offline: { type: 'danger', labelKey: 'dashboard.modulePanels.status.offline' },
}

function resolveAlarmType(alarmType: string | null) {
  if (!alarmType) {
    return '--'
  }
  const translated = t(`alarms.types.${alarmType}`)
  return translated === `alarms.types.${alarmType}` ? alarmType : translated
}
</script>

<style scoped>
.module-card {
  display: grid;
  gap: 18px;
  padding: 18px;
  border: 1px solid var(--pal-line);
  border-radius: var(--pal-radius-lg);
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.04), rgba(255, 255, 255, 0.01)),
    rgba(6, 18, 25, 0.72);
  box-shadow: 0 14px 30px rgba(0, 0, 0, 0.12);
}

.module-card__head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.module-card__identity p,
.module-card__identity span {
  margin: 0;
  color: var(--pal-text-muted);
}

.module-card__identity strong {
  display: block;
  margin: 4px 0;
  font-size: 1.1rem;
}

.module-card__grid {
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.module-card__metric {
  display: grid;
  gap: 4px;
  padding: 12px 14px;
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: var(--pal-radius-md);
  background: rgba(255, 255, 255, 0.02);
}

.module-card__metric span {
  color: var(--pal-text-muted);
  font-size: 0.82rem;
}

.module-card__metric strong {
  font-size: 0.98rem;
  line-height: 1.4;
}

:root[data-theme='light'] .module-card {
  border-color: rgba(19, 72, 96, 0.14);
  background:
    radial-gradient(circle at top right, rgba(14, 165, 183, 0.14), transparent 32%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.96), rgba(240, 247, 249, 0.92));
  box-shadow:
    0 18px 34px rgba(76, 111, 126, 0.16),
    inset 0 1px 0 rgba(255, 255, 255, 0.72);
}

:root[data-theme='light'] .module-card__identity p,
:root[data-theme='light'] .module-card__identity span,
:root[data-theme='light'] .module-card__metric span {
  color: var(--pal-text-muted);
}

:root[data-theme='light'] .module-card__identity strong,
:root[data-theme='light'] .module-card__metric strong {
  color: var(--pal-text);
}

:root[data-theme='light'] .module-card__metric {
  border-color: rgba(19, 72, 96, 0.1);
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.88), rgba(234, 242, 245, 0.82));
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.58);
}

@media (max-width: 640px) {
  .module-card__head {
    flex-direction: column;
    align-items: flex-start;
  }

  .module-card__grid {
    grid-template-columns: 1fr;
  }
}
</style>
