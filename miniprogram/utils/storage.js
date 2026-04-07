const TOKEN_KEY = 'pal4g-miniprogram-token'
const PROFILE_KEY = 'pal4g-miniprogram-profile'
const SUBSCRIPTION_KEY = 'pal4g-miniprogram-subscription'
const SERVICE_ORIGIN_KEY = 'pal4g-miniprogram-service-origin'

export function getToken() {
  return uni.getStorageSync(TOKEN_KEY) || ''
}

export function setToken(token) {
  uni.setStorageSync(TOKEN_KEY, token)
}

export function clearToken() {
  uni.removeStorageSync(TOKEN_KEY)
}

export function getProfile() {
  return uni.getStorageSync(PROFILE_KEY) || null
}

export function setProfile(profile) {
  uni.setStorageSync(PROFILE_KEY, profile)
}

export function clearProfile() {
  uni.removeStorageSync(PROFILE_KEY)
}

export function getSubscriptionState() {
  return (
    uni.getStorageSync(SUBSCRIPTION_KEY) || {
      enabled: false,
      templateIds: [],
      availableTemplateIds: [],
      subscribedAt: '',
      unsubscribedAt: '',
      updatedAt: '',
      source: 'server',
    }
  )
}

export function setSubscriptionState(state) {
  uni.setStorageSync(SUBSCRIPTION_KEY, state)
}

export function clearSubscriptionState() {
  uni.removeStorageSync(SUBSCRIPTION_KEY)
}

export function getServiceOrigin() {
  return String(uni.getStorageSync(SERVICE_ORIGIN_KEY) || '').trim()
}

export function setServiceOrigin(origin) {
  uni.setStorageSync(SERVICE_ORIGIN_KEY, origin)
}

export function clearServiceOrigin() {
  uni.removeStorageSync(SERVICE_ORIGIN_KEY)
}

export function clearSessionStorage() {
  clearToken()
  clearProfile()
  clearSubscriptionState()
}
