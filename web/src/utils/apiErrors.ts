import type { LocaleCode } from '@/types/domain'

const backendErrorLabelKeys: Record<string, string> = {
  'Access denied': 'apiErrors.accessDenied',
  'Alarm not found': 'apiErrors.alarmNotFound',
  'Current admin cannot deactivate self': 'apiErrors.currentAdminCannotDeactivateSelf',
  'Current admin cannot delete self': 'apiErrors.currentAdminCannotDeleteSelf',
  'Current password is incorrect': 'apiErrors.currentPasswordIncorrect',
  'Database backup currently only supports sqlite+aiosqlite': 'apiErrors.databaseBackupOnlySqlite',
  'Database file does not exist': 'apiErrors.databaseFileMissing',
  'Device group name already exists': 'apiErrors.deviceGroupNameExists',
  'Device group not found': 'apiErrors.deviceGroupNotFound',
  'Device group still has assigned devices': 'apiErrors.deviceGroupHasDevices',
  'Device is already bound to another user': 'apiErrors.deviceAlreadyBound',
  'Device not found': 'apiErrors.deviceNotFound',
  'Device serial number already exists': 'apiErrors.deviceSerialExists',
  'Device still has modules and cannot be deleted': 'apiErrors.deviceHasModules',
  'Incorrect username or password': 'apiErrors.incorrectUsernameOrPassword',
  'Invalid authentication credentials': 'apiErrors.invalidCredentials',
  'Module code already exists in this device': 'apiErrors.moduleCodeExistsInDevice',
  'Module has historical records and cannot be deleted': 'apiErrors.moduleHasHistory',
  'Module not found': 'apiErrors.moduleNotFound',
  'Protocol profile is inactive': 'apiErrors.protocolProfileInactive',
  'Protocol profile name already exists': 'apiErrors.protocolProfileNameExists',
  'Protocol profile not found': 'apiErrors.protocolProfileNotFound',
  'Relay command not found': 'apiErrors.relayCommandNotFound',
  'Super admin access required': 'apiErrors.superAdminRequired',
  'User is inactive': 'apiErrors.userInactive',
  'User is inactive or does not exist': 'apiErrors.userInactiveOrMissing',
  'User not found': 'apiErrors.userNotFound',
  'User still owns device groups and cannot be deleted': 'apiErrors.userOwnsDeviceGroups',
  'User still owns devices and cannot be deleted': 'apiErrors.userOwnsDevices',
  'Username already exists': 'apiErrors.usernameExists',
}

function isChineseText(value: string) {
  return /[\u3400-\u9fff]/.test(value)
}

function extractErrorDetail(error: unknown) {
  const detail = (error as any)?.response?.data?.detail
  return typeof detail === 'string' && detail.trim() ? detail.trim() : ''
}

export function resolveApiErrorMessage(
  error: unknown,
  locale: LocaleCode,
  t: (path: string) => string,
  fallback: string,
) {
  const detail = extractErrorDetail(error)
  if (!detail) {
    return fallback
  }

  if (locale !== 'zh-CN') {
    return detail
  }

  if (isChineseText(detail)) {
    return detail
  }

  const labelKey = backendErrorLabelKeys[detail]
  return labelKey ? t(labelKey) : fallback
}
