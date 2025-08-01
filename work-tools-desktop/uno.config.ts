import { defineConfig, presetUno, presetTypography } from "unocss";

export default defineConfig({
	presets: [presetUno(), presetTypography()],
	theme: {
		colors: {
			// 苹果风格主色调
			primary: {
				DEFAULT: "#007AFF",
				hover: "#0051D5",
				active: "#003D9F",
				light: "#B3D9FF",
			},
			secondary: "#5856D6",
			success: "#34C759",
			warning: "#FF9500",
			error: "#FF3B30",

			// 文本颜色
			text: {
				primary: "#1d1d1f",
				secondary: "#6e6e73",
				tertiary: "#8e8e93",
			},

			// 背景颜色
			background: {
				primary: "#ffffff",
				secondary: "#f8f9fa",
				tertiary: "#f2f2f7",
			},

			// 边框颜色
			border: {
				primary: "rgba(0, 0, 0, 0.1)",
				secondary: "rgba(0, 0, 0, 0.05)",
			},

			// 覆盖层
			overlay: "rgba(0, 0, 0, 0.4)",
		},
		spacing: {
			xs: "4px",
			sm: "8px",
			md: "12px",
			lg: "16px",
			xl: "20px",
			"2xl": "24px",
			"3xl": "32px",
		},
		borderRadius: {
			sm: "4px",
			md: "8px",
			lg: "12px",
			xl: "16px",
		},
		fontSize: {
			xs: "11px",
			sm: "12px",
			base: "14px",
			lg: "16px",
			xl: "18px",
			"2xl": "20px",
			"3xl": "24px",
		},
		fontWeight: {
			normal: "400",
			medium: "500",
			semibold: "600",
			bold: "700",
		},
		fontFamily: {
			primary:
				"PingFang SC, SF Pro Display, SF Pro Text, system-ui, -apple-system, BlinkMacSystemFont, Helvetica Neue, Microsoft YaHei UI, Segoe UI, Arial, sans-serif",
			mono: "SF Mono, Monaco, Inconsolata, Roboto Mono, Source Code Pro, monospace",
		},
		boxShadow: {
			sm: "0 1px 3px rgba(0, 0, 0, 0.1)",
			md: "0 4px 6px rgba(0, 0, 0, 0.1)",
			lg: "0 10px 15px rgba(0, 0, 0, 0.1)",
		},
	},
	// 自定义配置
	safelist: ["duration-150", "duration-250", "duration-350"],
	shortcuts: {
		// 按钮样式快捷方式
		"btn-base":
			"inline-flex items-center justify-center px-lg py-sm border border-border-primary rounded-md font-primary text-base font-semibold cursor-pointer transition-all duration-150",
		"btn-primary":
			"btn-base bg-primary text-white border-primary-hover hover:bg-primary-hover",
		"btn-secondary":
			"btn-base bg-background-primary text-text-primary hover:bg-background-secondary",
		"btn-sm": "px-md py-xs text-sm",

		// 输入框样式
		"input-base":
			"px-lg py-md border border-border-primary rounded-md font-primary text-base bg-background-primary text-text-primary transition-all duration-150 focus:outline-none focus:border-primary focus:bg-white",

		// 表格样式
		"table-base": "w-full border-collapse text-sm",
		"table-header": "bg-background-secondary font-semibold text-text-primary",
		"table-cell": "px-md py-sm text-left border-b border-border-secondary",
		"table-row-hover": "hover:bg-background-secondary",

		// 页面布局
		"page-container":
			"flex flex-col h-screen bg-background-primary overflow-hidden",
		"page-header":
			"flex-shrink-0 bg-gradient-to-b from-background-secondary to-background-primary border-b border-border-primary px-3xl py-xl",
		"page-toolbar":
			"flex-shrink-0 flex items-center gap-lg px-3xl py-lg bg-background-secondary border-b border-border-primary",
		"page-main":
			"flex-1 flex flex-col overflow-hidden px-3xl py-lg max-w-screen-2xl mx-auto w-full",
		"page-content":
			"flex-1 flex flex-col overflow-hidden bg-background-primary rounded-lg border border-border-secondary",
		"page-footer":
			"flex-shrink-0 flex justify-between items-center px-3xl py-md bg-background-secondary border-t border-border-primary text-sm",

		// 工具栏组件
		"toolbar-section": "flex items-center gap-md",
		"toolbar-divider": "w-px h-6 bg-border-primary mx-sm",

		// 状态样式
		"loading-spinner": "animate-spin",
		"drag-over": "bg-primary/5 relative",

		// 响应式隐藏
		"hidden-mobile": "hidden md:block",
		"hidden-desktop": "block md:hidden",
	},
	rules: [
		// 自定义规则
		[
			/^bg-gradient-apple$/,
			() => ({
				background:
					"linear-gradient(to bottom, rgba(248, 249, 250, 1.0), rgba(255, 255, 255, 1.0))",
			}),
		],
		[
			/^btn-gradient$/,
			() => ({
				background:
					"linear-gradient(to bottom, rgba(255, 255, 255, 0.9), rgba(245, 245, 247, 0.9))",
			}),
		],
		// vxe-table 样式定制
		[
			/^file-table$/,
			() => ({
				"--vxe-table-font-size": "var(--un-font-size-base)",
				"--vxe-table-header-font-size": "var(--un-font-size-base)",
				"--vxe-table-footer-font-size": "var(--un-font-size-base)",
				"--vxe-table-row-height": "40px",
				"--vxe-table-header-row-height": "44px",
				"--vxe-table-footer-row-height": "40px",
				"--vxe-table-border-radius": "var(--un-border-radius-md)",
				"--vxe-table-border-width": "1px",
				"--vxe-table-border-color": "var(--un-color-border-primary)",
				"--vxe-table-header-border-color": "var(--un-color-border-primary)",
				"--vxe-table-footer-border-color": "var(--un-color-border-primary)",
				"--vxe-table-header-background-color":
					"var(--un-color-background-secondary)",
				"--vxe-table-body-background-color":
					"var(--un-color-background-primary)",
				"--vxe-table-footer-background-color":
					"var(--un-color-background-secondary)",
				"--vxe-table-row-hover-background-color":
					"var(--un-color-background-secondary)",
				"--vxe-table-row-current-background-color":
					"var(--un-color-primary-light)",
				"--vxe-table-row-hover-current-background-color":
					"var(--un-color-primary-light)",
				"--vxe-table-column-hover-background-color":
					"var(--un-color-background-secondary)",
				"--vxe-table-column-current-background-color":
					"var(--un-color-primary-light)",
				"--vxe-table-cell-padding-left": "var(--un-spacing-md)",
				"--vxe-table-cell-padding-right": "var(--un-spacing-md)",
				"--vxe-table-resizable-line-color": "var(--un-color-primary)",
				"--vxe-table-checkbox-range-background-color":
					"var(--un-color-primary-light)",
			}),
		],
	],
});
