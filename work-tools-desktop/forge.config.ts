import type { ForgeConfig } from "@electron-forge/shared-types";
import { MakerSquirrel } from "@electron-forge/maker-squirrel";
import { VitePlugin } from "@electron-forge/plugin-vite";
import { FusesPlugin } from "@electron-forge/plugin-fuses";
import { FuseV1Options, FuseVersion } from "@electron/fuses";

const config: ForgeConfig = {
	packagerConfig: {
		asar: true,
		icon: "./assets/icon",
		name: "工作工具",
		executableName: "work-tools",
		appBundleId: "com.work-tools.desktop",
		appCategoryType: "public.app-category.productivity",
		win32metadata: {
			CompanyName: "Work Tools Team",
			FileDescription: "批量文件处理工具",
			ProductName: "工作工具",
		},
	},
	rebuildConfig: {},
	makers: [
		new MakerSquirrel({
			name: "work-tools",
			authors: "Work Tools Team",
			description: "批量文件处理工具 - 文件匹配和重命名助手",
		}),
	],
	plugins: [
		new VitePlugin({
			build: [
				{
					entry: "src/main/main.ts",
					config: "vite.main.config.ts",
					target: "main",
				},
				{
					entry: "src/main/preload.ts",
					config: "vite.preload.config.ts",
					target: "preload",
				},
			],
			renderer: [
				{
					name: "main_window",
					config: "vite.renderer.config.ts",
				},
			],
		}),
		new FusesPlugin({
			version: FuseVersion.V1,
			[FuseV1Options.RunAsNode]: false,
			[FuseV1Options.EnableCookieEncryption]: true,
			[FuseV1Options.EnableNodeOptionsEnvironmentVariable]: false,
			[FuseV1Options.EnableNodeCliInspectArguments]: false,
			[FuseV1Options.EnableEmbeddedAsarIntegrityValidation]: true,
			[FuseV1Options.OnlyLoadAppFromAsar]: true,
		}),
	],
};

export default config;
