import type { LocaleCode } from '@/types/domain'

const LOCALE_KEY = 'pal4g-locale'

const errorMessageMap: Record<string, { 'zh-CN': string; 'en-US': string }> = {
  'Incorrect username or password': {
    'zh-CN': '用户名或密码错误',
    'en-US': 'Incorrect username or password',
  },
  'User is inactive': {
    'zh-CN': '当前账号已被停用',
    'en-US': 'User is inactive',
  },
  'Invalid authentication credentials': {
    'zh-CN': '登录状态无效，请重新登录',
    'en-US': 'Invalid authentication credentials',
  },
  'User is inactive or does not exist': {
    'zh-CN': '账号不存在或已被停用',
    'en-US': 'User is inactive or does not exist',
  },
  'Super admin access required': {
    'zh-CN': '需要超级管理员权限',
    'en-US': 'Super admin access required',
  },
  'Access denied': {
    'zh-CN': '无权执行当前操作',
    'en-US': 'Access denied',
  },
  'User not found': {
    'zh-CN': '用户不存在',
    'en-US': 'User not found',
  },
  'Device not found': {
    'zh-CN': '设备不存在',
    'en-US': 'Device not found',
  },
  'Module not found': {
    'zh-CN': '设备通道不存在',
    'en-US': 'Module not found',
  },
  'Alarm not found': {
    'zh-CN': '报警记录不存在',
    'en-US': 'Alarm not found',
  },
  'Relay command not found': {
    'zh-CN': '控制指令不存在',
    'en-US': 'Relay command not found',
  },
  'Protocol profile not found': {
    'zh-CN': '通信协议模板不存在',
    'en-US': 'Protocol profile not found',
  },
  'Protocol profile is inactive': {
    'zh-CN': '通信协议模板已停用',
    'en-US': 'Protocol profile is inactive',
  },
  'Username already exists': {
    'zh-CN': '用户名已存在',
    'en-US': 'Username already exists',
  },
  'Device serial number already exists': {
    'zh-CN': '设备编号已存在',
    'en-US': 'Device serial number already exists',
  },
  'Device group name already exists': {
    'zh-CN': '设备分组名称已存在',
    'en-US': 'Device group name already exists',
  },
  'Module code already exists in this device': {
    'zh-CN': '该设备下的通道编码已存在',
    'en-US': 'Module code already exists in this device',
  },
  'Current admin cannot deactivate self': {
    'zh-CN': '不能停用当前登录账号',
    'en-US': 'Current admin cannot deactivate self',
  },
  'Current admin cannot delete self': {
    'zh-CN': '不能删除当前登录账号',
    'en-US': 'Current admin cannot delete self',
  },
  'User still owns devices': {
    'zh-CN': '该用户名下仍有设备，无法删除',
    'en-US': 'User still owns devices',
  },
  'User still owns device groups': {
    'zh-CN': '该用户名下仍有设备分组，无法删除',
    'en-US': 'User still owns device groups',
  },
  'Device already has an owner': {
    'zh-CN': '该设备已分配负责人',
    'en-US': 'Device already has an owner',
  },
  'Device has no owner': {
    'zh-CN': '该设备当前没有负责人',
    'en-US': 'Device has no owner',
  },
  'Device already has its primary channel': {
    'zh-CN': '该设备已存在主通道，不能重复添加',
    'en-US': 'Device already has its primary channel',
  },
  'Device still has channels attached': {
    'zh-CN': '该设备仍有关联通道，无法删除',
    'en-US': 'Device still has channels attached',
  },
  'Module has related history records and cannot be deleted': {
    'zh-CN': '该通道已有历史记录，无法删除',
    'en-US': 'Module has related history records and cannot be deleted',
  },
}

function resolveLocale(): LocaleCode {
  const savedLocale = localStorage.getItem(LOCALE_KEY)
  return savedLocale === 'en-US' ? 'en-US' : 'zh-CN'
}

function isChineseLocale(locale: LocaleCode) {
  return locale === 'zh-CN'
}

export function localizeErrorDetail(detail: unknown): unknown {
  const locale = resolveLocale()

  if (Array.isArray(detail)) {
    return isChineseLocale(locale) ? '请求参数不正确，请检查后重试' : 'Invalid request data'
  }

  if (typeof detail !== 'string' || !detail.trim()) {
    return detail
  }

  const normalizedDetail = detail.trim()
  const mappedMessage = errorMessageMap[normalizedDetail]
  if (mappedMessage) {
    return mappedMessage[locale]
  }

  if (isChineseLocale(locale)) {
    if (normalizedDetail.includes('not found')) {
      return '请求的数据不存在'
    }
    if (normalizedDetail.includes('already exists')) {
      return '数据已存在，请勿重复提交'
    }
    if (normalizedDetail.includes('access denied')) {
      return '无权执行当前操作'
    }
  }

  return normalizedDetail
}

export function localizeTransportError(message: string) {
  const locale = resolveLocale()
  if (locale === 'en-US') {
    return message
  }

  if (message.includes('timeout')) {
    return '请求超时，请稍后重试'
  }
  if (message.includes('Network Error')) {
    return '网络连接异常，请检查服务是否已启动'
  }
  return '请求失败，请稍后重试'
}
