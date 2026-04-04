import { computed } from 'vue'

import { messages } from '@/i18n/messages'
import { useSettingsStore } from '@/stores/settings'

function resolvePath(path: string, locale: string) {
  const segments = path.split('.')
  const resolveFromLocale = (targetLocale: string) => {
    let current: any = messages[targetLocale as keyof typeof messages]

    for (const segment of segments) {
      if (current && typeof current === 'object' && segment in current) {
        current = current[segment]
      } else {
        return null
      }
    }

    return typeof current === 'string' ? current : null
  }

  if (locale === 'zh-CN') {
    return resolveFromLocale(locale) ?? path
  }

  return resolveFromLocale(locale) ?? resolveFromLocale('en-US') ?? path
}

export function useI18n() {
  const settingsStore = useSettingsStore()

  const locale = computed(() => settingsStore.localeCode)

  function t(path: string) {
    return resolvePath(path, locale.value)
  }

  return {
    locale,
    t,
  }
}
