import { request } from '@/api/http'

export function getMiniHomeApi() {
  return request({
    url: '/dashboard/my/home',
  })
}

export function getMyDevicesApi() {
  return request({
    url: '/dashboard/my/devices',
  })
}

export function getMyRecentAlarmsApi(limit = 6) {
  return request({
    url: '/dashboard/my/alarms',
    data: {
      limit,
    },
  })
}

export function getAlarmPageApi(params) {
  return request({
    url: '/dashboard/alarms/page',
    data: params,
  })
}

export function getDeviceDashboardDetailApi(deviceId) {
  return request({
    url: `/dashboard/devices/${deviceId}`,
  })
}
