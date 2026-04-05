export function extractErrorMessage(error, fallback = '操作失败，请稍后重试') {
  if (!error) {
    return fallback
  }

  if (typeof error === 'string') {
    return error
  }

  if (typeof error.detail === 'string' && error.detail.trim()) {
    return error.detail.trim()
  }

  if (typeof error.message === 'string' && error.message.trim()) {
    return error.message.trim()
  }

  return fallback
}

export function showRequestError(error, fallback) {
  uni.showToast({
    title: extractErrorMessage(error, fallback),
    icon: 'none',
    duration: 2200,
  })
}
