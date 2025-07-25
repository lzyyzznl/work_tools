// See the Electron documentation for details on how to use preload scripts:
// https://www.electronjs.org/docs/latest/tutorial/process-model#preload-scripts

import { contextBridge, ipcRenderer } from 'electron';

// 文件系统 API 接口定义
interface FileSelectOptions {
  multiple?: boolean;
  filters?: Array<{ name: string; extensions: string[] }>;
}

interface FileData {
  name: string;
  path: string;
  size: number;
  lastModified: number;
  type: string;
  arrayBuffer: ArrayBuffer;
}

interface FileOperationResult {
  success: boolean;
  message?: string;
  error?: string;
}

// 暴露安全的 API 到渲染进程
contextBridge.exposeInMainWorld('electronAPI', {
  fileSystem: {
    selectFiles: async (options: FileSelectOptions = {}): Promise<File[]> => {
      try {
        const fileDataArray: FileData[] = await ipcRenderer.invoke('file-system:select-files', options);

        // 将文件数据转换为 File 对象
        const files: File[] = [];
        for (const fileData of fileDataArray) {
          const blob = new Blob([fileData.arrayBuffer], { type: fileData.type });
          const file = new File([blob], fileData.name, {
            type: fileData.type,
            lastModified: fileData.lastModified
          });

          // 添加路径信息（非标准属性，但在 Electron 环境中有用）
          Object.defineProperty(file, 'path', {
            value: fileData.path,
            writable: false,
            enumerable: false
          });

          files.push(file);
        }

        return files;
      } catch (error) {
        console.error('Error selecting files:', error);
        throw error;
      }
    },

    selectDirectory: async (): Promise<File[]> => {
      try {
        const fileDataArray: FileData[] = await ipcRenderer.invoke('file-system:select-directory');

        // 将文件数据转换为 File 对象
        const files: File[] = [];
        for (const fileData of fileDataArray) {
          const blob = new Blob([fileData.arrayBuffer], { type: fileData.type });
          const file = new File([blob], fileData.name, {
            type: fileData.type,
            lastModified: fileData.lastModified
          });

          // 添加路径信息
          Object.defineProperty(file, 'path', {
            value: fileData.path,
            writable: false,
            enumerable: false
          });

          files.push(file);
        }

        return files;
      } catch (error) {
        console.error('Error selecting directory:', error);
        throw error;
      }
    },

    readFile: async (path: string): Promise<ArrayBuffer> => {
      try {
        return await ipcRenderer.invoke('file-system:read-file', path);
      } catch (error) {
        console.error('Error reading file:', error);
        throw error;
      }
    },

    writeFile: async (path: string, data: ArrayBuffer): Promise<FileOperationResult> => {
      try {
        return await ipcRenderer.invoke('file-system:write-file', path, data);
      } catch (error) {
        console.error('Error writing file:', error);
        throw error;
      }
    }
  }
});
