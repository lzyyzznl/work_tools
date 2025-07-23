<script setup lang="ts">
import { ref, computed } from 'vue'
import { useKeyboardShortcuts } from '../../composables/useKeyboardShortcuts'

interface Props {
  modelValue: boolean
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const { getShortcuts, getShortcutDisplayText } = useKeyboardShortcuts()

const activeTab = ref('overview')

const isVisible = computed({
  get: () => props.modelValue,
  set: (value: boolean) => emit('update:modelValue', value)
})

const shortcuts = computed(() => getShortcuts())

function closeModal() {
  isVisible.value = false
}

function switchTab(tabKey: string) {
  activeTab.value = tabKey
}

const helpSections = [
  {
    key: 'overview',
    title: '概述',
    icon: '📖'
  },
  {
    key: 'features',
    title: '功能介绍',
    icon: '✨'
  },
  {
    key: 'shortcuts',
    title: '快捷键',
    icon: '⌨️'
  },
  {
    key: 'tips',
    title: '使用技巧',
    icon: '💡'
  },
  {
    key: 'faq',
    title: '常见问题',
    icon: '❓'
  }
]
</script>

<template>
  <div v-if="isVisible" class="modal-overlay" @click="closeModal">
    <div class="modal-container" @click.stop>
      <!-- 模态框头部 -->
      <div class="modal-header">
        <h2 class="modal-title">
          <span class="modal-icon">📚</span>
          帮助文档
        </h2>
        <button class="modal-close" @click="closeModal">×</button>
      </div>

      <!-- 模态框内容 -->
      <div class="modal-content">
        <!-- 标签页导航 -->
        <div class="tabs-nav">
          <button
            v-for="section in helpSections"
            :key="section.key"
            :class="['tab-button', { active: activeTab === section.key }]"
            @click="switchTab(section.key)"
          >
            <span class="tab-icon">{{ section.icon }}</span>
            <span class="tab-label">{{ section.title }}</span>
          </button>
        </div>

        <!-- 标签页内容 -->
        <div class="tabs-content">
          <!-- 概述 -->
          <div v-show="activeTab === 'overview'" class="tab-panel">
            <div class="help-section">
              <h3>欢迎使用文件重命名工具</h3>
              <p>这是一个强大的批量文件重命名工具，支持多种重命名模式和实时预览功能。</p>
              
              <h4>主要特性</h4>
              <ul>
                <li>🔄 字符串替换 - 查找并替换文件名中的指定文本</li>
                <li>➕ 添加前缀/后缀 - 在文件名前后添加文本</li>
                <li>🔢 批量添加序号 - 为文件添加自动递增的序号</li>
                <li>✂️ 删除字符 - 从文件名中删除指定位置的字符</li>
                <li>👁️ 实时预览 - 修改参数时自动显示重命名效果</li>
                <li>↩️ 撤回功能 - 支持撤回最近的重命名操作</li>
                <li>⌨️ 快捷键支持 - 提供丰富的键盘快捷键</li>
              </ul>

              <h4>使用流程</h4>
              <ol>
                <li>选择要重命名的文件或文件夹</li>
                <li>选择重命名模式（替换、添加、序号、删除）</li>
                <li>配置重命名参数</li>
                <li>查看预览效果</li>
                <li>执行重命名操作</li>
              </ol>
            </div>
          </div>

          <!-- 功能介绍 -->
          <div v-show="activeTab === 'features'" class="tab-panel">
            <div class="help-section">
              <h3>功能详细介绍</h3>

              <div class="feature-item">
                <h4>🔄 字符串替换</h4>
                <p>查找文件名中的指定字符串并替换为新的字符串。支持精确匹配，区分大小写。</p>
                <div class="example">
                  <strong>示例：</strong>将 "IMG_20240115_001.jpg" 中的 "IMG_" 替换为 "Photo_"<br>
                  <strong>结果：</strong>"Photo_20240115_001.jpg"
                </div>
              </div>

              <div class="feature-item">
                <h4>➕ 添加前缀/后缀</h4>
                <p>在文件名的开头或扩展名之前添加指定的文本内容。</p>
                <div class="example">
                  <strong>前缀示例：</strong>为 "document.txt" 添加前缀 "backup_"<br>
                  <strong>结果：</strong>"backup_document.txt"<br>
                  <strong>后缀示例：</strong>为 "document.txt" 添加后缀 "_v2"<br>
                  <strong>结果：</strong>"document_v2.txt"
                </div>
              </div>

              <div class="feature-item">
                <h4>🔢 批量添加序号</h4>
                <p>为文件添加自动递增的序号，支持自定义起始数字、位数、步长和分隔符。</p>
                <div class="example">
                  <strong>示例：</strong>起始数字1，3位数，步长1，分隔符"_"<br>
                  <strong>结果：</strong>"001_document.txt", "002_document.txt", "003_document.txt"
                </div>
              </div>

              <div class="feature-item">
                <h4>✂️ 删除字符</h4>
                <p>从文件名中删除指定位置和数量的字符，支持从左侧或右侧删除。</p>
                <div class="example">
                  <strong>示例：</strong>从左侧第1个位置删除4个字符<br>
                  <strong>原文件：</strong>"IMG_document.txt"<br>
                  <strong>结果：</strong>"document.txt"
                </div>
              </div>
            </div>
          </div>

          <!-- 快捷键 -->
          <div v-show="activeTab === 'shortcuts'" class="tab-panel">
            <div class="help-section">
              <h3>键盘快捷键</h3>
              <p>使用快捷键可以大大提高操作效率。以下是所有可用的快捷键：</p>

              <div class="shortcuts-list">
                <div
                  v-for="shortcut in shortcuts"
                  :key="shortcut.description"
                  class="shortcut-item"
                >
                  <div class="shortcut-keys">
                    {{ getShortcutDisplayText(shortcut) }}
                  </div>
                  <div class="shortcut-description">
                    {{ shortcut.description }}
                  </div>
                </div>
              </div>

              <div class="shortcut-note">
                <p><strong>注意：</strong></p>
                <ul>
                  <li>快捷键在输入框获得焦点时可能不会生效</li>
                  <li>可以在设置中禁用快捷键功能</li>
                  <li>Escape键可以取消当前操作或关闭对话框</li>
                </ul>
              </div>
            </div>
          </div>

          <!-- 使用技巧 -->
          <div v-show="activeTab === 'tips'" class="tab-panel">
            <div class="help-section">
              <h3>使用技巧</h3>

              <div class="tip-item">
                <h4>💡 批量处理技巧</h4>
                <ul>
                  <li>使用拖拽功能可以快速添加文件</li>
                  <li>支持同时选择文件和文件夹</li>
                  <li>可以使用Ctrl+A全选所有文件</li>
                  <li>建议在执行前先预览效果</li>
                </ul>
              </div>

              <div class="tip-item">
                <h4>🎯 重命名策略</h4>
                <ul>
                  <li>对于大量文件，建议使用序号模式</li>
                  <li>替换模式适合统一修改文件名格式</li>
                  <li>删除模式可以快速清理文件名前缀</li>
                  <li>组合使用多种模式可以实现复杂的重命名需求</li>
                </ul>
              </div>

              <div class="tip-item">
                <h4>⚡ 性能优化</h4>
                <ul>
                  <li>处理大量文件时可以关闭自动预览</li>
                  <li>在设置中调整每页显示的文件数量</li>
                  <li>使用虚拟滚动处理超大文件列表</li>
                  <li>定期清理操作历史记录</li>
                </ul>
              </div>

              <div class="tip-item">
                <h4>🔒 安全建议</h4>
                <ul>
                  <li>重要文件建议先备份</li>
                  <li>使用预览功能确认重命名效果</li>
                  <li>利用撤回功能恢复误操作</li>
                  <li>避免使用系统保留字符</li>
                </ul>
              </div>
            </div>
          </div>

          <!-- 常见问题 -->
          <div v-show="activeTab === 'faq'" class="tab-panel">
            <div class="help-section">
              <h3>常见问题</h3>

              <div class="faq-item">
                <h4>Q: 为什么有些文件无法重命名？</h4>
                <p>A: 可能的原因包括：文件正在被其他程序使用、没有足够的权限、文件名包含非法字符、或者文件被系统保护。</p>
              </div>

              <div class="faq-item">
                <h4>Q: 如何撤回重命名操作？</h4>
                <p>A: 点击工具栏中的"撤回"按钮，或使用快捷键Ctrl+Z。注意撤回功能只能恢复最近的操作。</p>
              </div>

              <div class="faq-item">
                <h4>Q: 预览显示的结果和实际重命名结果不一致？</h4>
                <p>A: 这可能是由于文件系统限制或文件名冲突导致的。建议检查文件名是否包含非法字符或与现有文件重名。</p>
              </div>

              <div class="faq-item">
                <h4>Q: 如何处理大量文件时的性能问题？</h4>
                <p>A: 可以在设置中关闭自动预览、启用虚拟滚动、或减少每页显示的文件数量来提高性能。</p>
              </div>

              <div class="faq-item">
                <h4>Q: 支持哪些文件格式？</h4>
                <p>A: 工具支持所有类型的文件和文件夹，重命名操作只修改文件名，不会影响文件内容。</p>
              </div>

              <div class="faq-item">
                <h4>Q: 如何备份和恢复设置？</h4>
                <p>A: 在设置页面中可以导出当前设置到JSON文件，也可以从文件导入之前保存的设置。</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 模态框底部 -->
      <div class="modal-footer">
        <div class="footer-info">
          <span class="version-info">版本 1.0.0</span>
        </div>
        <div class="footer-actions">
          <button class="btn btn-primary" @click="closeModal">
            关闭
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: var(--spacing-lg);
}

.modal-container {
  background: var(--color-background-primary);
  border-radius: var(--radius-lg);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
  width: 100%;
  max-width: 900px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-lg) var(--spacing-xl);
  border-bottom: 1px solid var(--color-border-primary);
  background: var(--color-background-secondary);

  .modal-title {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    margin: 0;
    font-size: var(--font-size-xl);
    font-weight: var(--font-weight-semibold);
    color: var(--color-text-primary);

    .modal-icon {
      font-size: var(--font-size-2xl);
    }
  }

  .modal-close {
    width: 32px;
    height: 32px;
    border: none;
    background: none;
    color: var(--color-text-secondary);
    font-size: var(--font-size-xl);
    cursor: pointer;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all var(--transition-fast);

    &:hover {
      background: var(--color-background-tertiary);
      color: var(--color-text-primary);
    }
  }
}

.modal-content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.tabs-nav {
  width: 180px;
  background: var(--color-background-secondary);
  border-right: 1px solid var(--color-border-primary);
  padding: var(--spacing-md);
  overflow-y: auto;

  .tab-button {
    width: 100%;
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    padding: var(--spacing-sm) var(--spacing-md);
    border: none;
    background: none;
    color: var(--color-text-secondary);
    text-align: left;
    cursor: pointer;
    border-radius: var(--radius-md);
    transition: all var(--transition-fast);
    margin-bottom: var(--spacing-xs);

    &:hover {
      background: var(--color-background-tertiary);
      color: var(--color-text-primary);
    }

    &.active {
      background: var(--color-primary);
      color: white;
    }

    .tab-icon {
      font-size: var(--font-size-base);
    }

    .tab-label {
      font-size: var(--font-size-sm);
      font-weight: var(--font-weight-medium);
    }
  }
}

.tabs-content {
  flex: 1;
  overflow-y: auto;
  padding: var(--spacing-lg);
}

.help-section {
  h3 {
    margin: 0 0 var(--spacing-md) 0;
    font-size: var(--font-size-lg);
    font-weight: var(--font-weight-semibold);
    color: var(--color-text-primary);
  }

  h4 {
    margin: var(--spacing-lg) 0 var(--spacing-sm) 0;
    font-size: var(--font-size-base);
    font-weight: var(--font-weight-semibold);
    color: var(--color-text-primary);
  }

  p {
    margin: 0 0 var(--spacing-md) 0;
    line-height: 1.6;
    color: var(--color-text-secondary);
  }

  ul, ol {
    margin: 0 0 var(--spacing-md) 0;
    padding-left: var(--spacing-lg);
    color: var(--color-text-secondary);

    li {
      margin-bottom: var(--spacing-xs);
      line-height: 1.5;
    }
  }
}

.feature-item {
  margin-bottom: var(--spacing-xl);
  padding: var(--spacing-md);
  border: 1px solid var(--color-border-secondary);
  border-radius: var(--radius-md);
  background: var(--color-background-primary);

  .example {
    margin-top: var(--spacing-sm);
    padding: var(--spacing-sm);
    background: var(--color-background-secondary);
    border-radius: var(--radius-sm);
    font-size: var(--font-size-sm);
    font-family: var(--font-mono);
    color: var(--color-text-secondary);
  }
}

.shortcuts-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-lg);

  .shortcut-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--spacing-sm) var(--spacing-md);
    border: 1px solid var(--color-border-secondary);
    border-radius: var(--radius-sm);
    background: var(--color-background-primary);

    .shortcut-keys {
      font-family: var(--font-mono);
      font-size: var(--font-size-sm);
      font-weight: var(--font-weight-semibold);
      color: var(--color-primary);
      background: var(--color-background-secondary);
      padding: var(--spacing-xs) var(--spacing-sm);
      border-radius: var(--radius-sm);
    }

    .shortcut-description {
      font-size: var(--font-size-sm);
      color: var(--color-text-secondary);
    }
  }
}

.shortcut-note {
  padding: var(--spacing-md);
  background: rgba(0, 122, 255, 0.1);
  border-radius: var(--radius-md);
  border-left: 4px solid var(--color-primary);

  p {
    margin: 0 0 var(--spacing-sm) 0;
    font-weight: var(--font-weight-semibold);
    color: var(--color-primary);
  }

  ul {
    margin: 0;
    color: var(--color-text-secondary);
  }
}

.tip-item {
  margin-bottom: var(--spacing-lg);
  padding: var(--spacing-md);
  border: 1px solid var(--color-border-secondary);
  border-radius: var(--radius-md);
  background: var(--color-background-primary);
}

.faq-item {
  margin-bottom: var(--spacing-lg);
  padding: var(--spacing-md);
  border: 1px solid var(--color-border-secondary);
  border-radius: var(--radius-md);
  background: var(--color-background-primary);

  h4 {
    margin: 0 0 var(--spacing-sm) 0;
    color: var(--color-primary);
  }

  p {
    margin: 0;
  }
}

.modal-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-lg) var(--spacing-xl);
  border-top: 1px solid var(--color-border-primary);
  background: var(--color-background-secondary);

  .footer-info {
    .version-info {
      font-size: var(--font-size-sm);
      color: var(--color-text-tertiary);
    }
  }

  .footer-actions {
    display: flex;
    gap: var(--spacing-sm);
  }
}
</style>
