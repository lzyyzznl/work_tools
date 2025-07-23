import { ref, computed } from 'vue';

const STORAGE_KEY = 'file-matcher-search-history';
const MAX_HISTORY_SIZE = 20;

// 全局搜索历史状态
const searchHistory = ref<string[]>([]);

export function useSearchHistory() {
  
  /**
   * 加载搜索历史
   */
  async function loadSearchHistory() {
    try {
      const result = await chrome.storage.local.get([STORAGE_KEY]);
      const history = result[STORAGE_KEY] || [];
      searchHistory.value = Array.isArray(history) ? history : [];
    } catch (error) {
      console.error('加载搜索历史失败:', error);
      searchHistory.value = [];
    }
  }

  /**
   * 保存搜索历史
   */
  async function saveSearchHistory() {
    try {
      await chrome.storage.local.set({
        [STORAGE_KEY]: searchHistory.value
      });
    } catch (error) {
      console.error('保存搜索历史失败:', error);
    }
  }

  /**
   * 添加搜索记录
   */
  async function addSearchRecord(query: string) {
    if (!query || !query.trim()) return;
    
    const trimmedQuery = query.trim();
    
    // 移除已存在的相同记录
    const existingIndex = searchHistory.value.indexOf(trimmedQuery);
    if (existingIndex > -1) {
      searchHistory.value.splice(existingIndex, 1);
    }
    
    // 添加到开头
    searchHistory.value.unshift(trimmedQuery);
    
    // 限制历史记录数量
    if (searchHistory.value.length > MAX_HISTORY_SIZE) {
      searchHistory.value = searchHistory.value.slice(0, MAX_HISTORY_SIZE);
    }
    
    await saveSearchHistory();
  }

  /**
   * 删除搜索记录
   */
  async function removeSearchRecord(query: string) {
    const index = searchHistory.value.indexOf(query);
    if (index > -1) {
      searchHistory.value.splice(index, 1);
      await saveSearchHistory();
    }
  }

  /**
   * 清空搜索历史
   */
  async function clearSearchHistory() {
    searchHistory.value = [];
    await saveSearchHistory();
  }

  /**
   * 获取搜索建议
   */
  function getSearchSuggestions(query: string, limit: number = 5): string[] {
    if (!query || !query.trim()) {
      return searchHistory.value.slice(0, limit);
    }
    
    const trimmedQuery = query.trim().toLowerCase();
    return searchHistory.value
      .filter(item => item.toLowerCase().includes(trimmedQuery))
      .slice(0, limit);
  }

  /**
   * 计算属性：是否有搜索历史
   */
  const hasHistory = computed(() => searchHistory.value.length > 0);

  /**
   * 计算属性：最近的搜索记录
   */
  const recentSearches = computed(() => searchHistory.value.slice(0, 10));

  return {
    // 状态
    searchHistory: computed(() => searchHistory.value),
    hasHistory,
    recentSearches,
    
    // 方法
    loadSearchHistory,
    addSearchRecord,
    removeSearchRecord,
    clearSearchHistory,
    getSearchSuggestions,
  };
}
