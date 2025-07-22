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
  return `notification-${type}`
}
</script>

<template>
  <div class="notification-container">
    <transition-group name="notification" tag="div" class="notification-list">
      <div
        v-for="error in visibleErrors"
        :key="error.id"
        :class="['notification', getClassForType(error.type)]"
        @click="removeError(error.id)"
      >
        <div class="notification-icon">
          {{ getIconForType(error.type) }}
        </div>
        <div class="notification-content">
          <div class="notification-title">{{ error.title }}</div>
          <div class="notification-message">{{ error.message }}</div>
        </div>
        <button class="notification-close" @click.stop="removeError(error.id)">
          ×
        </button>
      </div>
    </transition-group>
  </div>
</template>

<style scoped lang="scss">
.notification-container {
  position: fixed;
  top: var(--spacing-lg);
  right: var(--spacing-lg);
  z-index: 1000;
  pointer-events: none;
}

.notification-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.notification {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-sm);
  min-width: 320px;
  max-width: 480px;
  padding: var(--spacing-md);
  border-radius: var(--radius-lg);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  cursor: pointer;
  pointer-events: auto;
  transition: all var(--transition-fast);

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
  }

  &.notification-error {
    background: rgba(255, 59, 48, 0.95);
    color: white;
    border-left: 4px solid #ff3b30;
  }

  &.notification-warning {
    background: rgba(255, 149, 0, 0.95);
    color: white;
    border-left: 4px solid #ff9500;
  }

  &.notification-info {
    background: rgba(0, 122, 255, 0.95);
    color: white;
    border-left: 4px solid #007aff;
  }

  &.notification-success {
    background: rgba(52, 199, 89, 0.95);
    color: white;
    border-left: 4px solid #34c759;
  }

  .notification-icon {
    flex-shrink: 0;
    font-size: var(--font-size-lg);
    margin-top: 2px;
  }

  .notification-content {
    flex: 1;
    min-width: 0;

    .notification-title {
      font-size: var(--font-size-sm);
      font-weight: var(--font-weight-semibold);
      margin-bottom: var(--spacing-xs);
      line-height: 1.3;
    }

    .notification-message {
      font-size: var(--font-size-sm);
      line-height: 1.4;
      opacity: 0.9;
      word-wrap: break-word;
    }
  }

  .notification-close {
    flex-shrink: 0;
    width: 24px;
    height: 24px;
    border: none;
    background: rgba(255, 255, 255, 0.2);
    color: inherit;
    border-radius: 50%;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: var(--font-size-lg);
    font-weight: bold;
    transition: background-color var(--transition-fast);

    &:hover {
      background: rgba(255, 255, 255, 0.3);
    }
  }
}

// 动画效果
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
