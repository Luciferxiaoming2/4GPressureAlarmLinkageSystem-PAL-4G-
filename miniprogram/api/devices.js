import { request } from '@/api/http'

export function getDeviceRuntimeApi(deviceId) {
  return request({
    url: `/devices/${deviceId}`,
  })
}

export function bindDeviceApi(payload) {
  return request({
    url: '/devices/bind',
    method: 'POST',
    data: payload,
    header: {
      'Content-Type': 'application/json',
    },
  })
}

export function unbindDeviceApi(deviceId) {
  return request({
    url: `/devices/${deviceId}/unbind`,
    method: 'POST',
  })
}

export function deleteDeviceApi(deviceId) {
  return request({
    url: `/devices/${deviceId}`,
    method: 'DELETE',
  })
}
