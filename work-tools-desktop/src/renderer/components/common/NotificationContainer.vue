<script setup lang="ts">
import { computed } from 'vue'
import { useErrorHandler } from '../../composables/useErrorHandler'

const { errors, removeError } = useErrorHandler()

const visibleErrors = computed(() => errors.value.slice(0, 5))

function getIconForType(type: string): string {
  switch (type) {
    case 'error':
      return '❌'
    case 'warning':
      return '⚠️'
    case 'info':
      return 'ℹ️'
    case 'success':
      return '✅'
    default:
      return 'ℹ️'
  }
}

function getClassForType(type: string): string {
  const baseClasses = 'flex items-start gap-3 min-w-80 max-w-120 p-4 rounded-lg shadow-lg cursor-pointer pointer-events-auto transition-all duration-200 hover:transform hover:-translate-y-0.5 hover:shadow-xl'
  
  switch (type) {
    case 'error':
      return `${baseClasses} bg-red-500/95 text-white border-l-4 border-red-600`
    case 'warning':
      return `${baseClasses} bg-orange-500/95 text-white border-l-4 border-orange-600`
    case 'info':
      return `${baseClasses} bg-blue-500/95 text-white border-l-4 border-blue-600`
    case 'success':
      return `${baseClasses} bg-green-500/95 text-white border-l-4 border-green-600`
    default:
      return `${baseClasses} bg-gray-500/95 text-white border-l-4 border-gray-600`
  }
}
</script>

<template>
  <div class="fixed top-6 right-6 z-1000 pointer-events-none">
    <transition-group 
      name="notification" 
      tag="div" 
      class="flex flex-col gap-3"
    >
      <div
        v-for="error in visibleErrors"
        :key="error.id"
        :class="getClassForType(error.type)"
        @click="removeError(error.id)"
      >
        <div class="flex-shrink-0 text-lg mt-0.5">
          {{ getIconForType(error.type) }}
        </div>
        <div class="flex-1 min-w-0">
          <div class="text-sm font-semibold mb-1 leading-tight">
            {{ error.title }}
          </div>
          <div class="text-sm leading-relaxed opacity-90 break-words">
            {{ error.message }}
          </div>
        </div>
        <button 
          class="flex-shrink-0 w-6 h-6 border-none bg-white/20 text-inherit rounded-full cursor-pointer flex items-center justify-center text-lg font-bold transition-colors duration-200 hover:bg-white/30"
          @click.stop="removeError(error.id)"
        >
          ×
        </button>
      </div>
    </transition-group>
  </div>
</template>

<style scoped>
/* 动画效果 */
.notification-enter-active,
.notification-leave-active {
  transition: all 0.3s ease;
}

.notification-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.notification-leave-to {
  opacity: 0;
  transform: translateX(100%);
}

.notification-move {
  transition: transform 0.3s ease;
}
</style>
