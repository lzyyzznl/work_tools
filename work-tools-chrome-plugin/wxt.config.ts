import { defineConfig } from "wxt";

// See https://wxt.dev/api/config.html
export default defineConfig({
	modules: ["@wxt-dev/module-vue"],
	manifest: {
		name: "批量文件处理工具",
		description: "文件匹配和重命名浏览器扩展 - 支持批量文件操作",
		version: "1.0.0",
		permissions: ["storage", "tabs"],
		host_permissions: ["file://*"],
	},
});
