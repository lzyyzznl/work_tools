import { ref } from 'vue'

export interface ErrorInfo {
  id: string
  type: 'error' | 'warning' | 'info' | 'success'
  title: string
  message: string
  timestamp: number
  duration?: number
}

export function useErrorHandler() {
  const errors = ref<ErrorInfo[]>([])
  const maxErrors = ref(10)

  function addError(error: Omit<ErrorInfo, 'id' | 'timestamp'>) {
    const errorInfo: ErrorInfo = {
      ...error,
      id: `error_${Date.now()}_${Math.random()}`,
      timestamp: Date.now(),
      duration: error.duration || (error.type === 'error' ? 5000 : 3000)
    }

    errors.value.unshift(errorInfo)

    // 限制错误数量
    if (errors.value.length > maxErrors.value) {
      errors.value = errors.value.slice(0, maxErrors.value)
    }

    // 自动移除
    if (errorInfo.duration && errorInfo.duration > 0) {
      setTimeout(() => {
        removeError(errorInfo.id)
      }, errorInfo.duration)
    }

    return errorInfo.id
  }

  function removeError(id: string) {
    const index = errors.value.findIndex(e => e.id === id)
    if (index > -1) {
      errors.value.splice(index, 1)
    }
  }

  function clearErrors() {
    errors.value = []
  }

  function handleError(error: any, context?: string) {
    console.error('Error in', context || 'unknown context', error)
    
    let message = '发生未知错误'
    let title = '错误'

    if (error instanceof Error) {
      message = error.message
      title = error.name || '错误'
    } else if (typeof error === 'string') {
      message = error
    } else if (error && typeof error === 'object') {
      message = error.message || error.toString()
      title = error.name || error.type || '错误'
    }

    return addError({
      type: 'error',
      title,
      message: context ? `${context}: ${message}` : message
    })
  }

  function handleSuccess(message: string, title = '成功') {
    return addError({
      type: 'success',
      title,
      message,
      duration: 3000
    })
  }

  function handleWarning(message: string, title = '警告') {
    return addError({
      type: 'warning',
      title,
      message,
      duration: 4000
    })
  }

  function handleInfo(message: string, title = '信息') {
    return addError({
      type: 'info',
      title,
      message,
      duration: 3000
    })
  }

  return {
    errors,
    maxErrors,
    addError,
    removeError,
    clearErrors,
    handleError,
    handleSuccess,
    handleWarning,
    handleInfo
  }
}
