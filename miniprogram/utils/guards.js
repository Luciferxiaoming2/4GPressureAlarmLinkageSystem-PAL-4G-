import { useAuthStore } from '@/stores/auth'

export async function ensureAuthenticated() {
  const authStore = useAuthStore()
  await authStore.initialize()

  if (authStore.isAuthenticated.value) {
    return true
  }

  uni.reLaunch({
    url: '/pages/login/index',
  })
  return false
}
