import { request } from '@/api/http'

export function createRelayCommandApi(payload) {
  return request({
    url: '/relay-commands',
    method: 'POST',
    data: payload,
    header: {
      'Content-Type': 'application/json',
    },
  })
}
