import { request } from '@/api/http'

export function changePasswordApi(payload) {
  return request({
    url: '/users/me/change-password',
    method: 'POST',
    data: payload,
    header: {
      'Content-Type': 'application/json',
    },
  })
}
