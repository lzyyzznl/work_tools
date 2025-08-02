// 主进程和预加载脚本特有的文件系统类型定义

// 文件数据（主进程和预加载脚本使用）
export interface FileData {
	name: string;
	path: string;
	size: number;
	lastModified: number;
	type: string;
	arrayBuffer: ArrayBuffer;
}
