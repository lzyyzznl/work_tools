import type { ForgeConfig } from "@electron-forge/shared-types";
import { MakerSquirrel } from "@electron-forge/maker-squirrel";
import { MakerZIP } from "@electron-forge/maker-zip";
import { MakerDeb } from "@electron-forge/maker-deb";
import { MakerRpm } from "@electron-forge/maker-rpm";
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
			setupIcon: "./assets/icon.ico",
			iconUrl: "./assets/icon.ico",
		}),
		new MakerZIP({}, ["darwin"]),
		new MakerRpm({
			options: {
				name: "work-tools",
				productName: "工作工具",
				description: "批量文件处理工具",
				homepage: "https://github.com/work-tools/desktop",
				license: "MIT",
			}
		}),
		new MakerDeb({
			options: {
				name: "work-tools",
				productName: "工作工具",
				description: "批量文件处理工具",
				homepage: "https://github.com/work-tools/desktop",
				maintainer: "Work Tools Team",
				section: "utils",
			}
		}),
	],
	plugins: [
		new VitePlugin({
			// `build` can specify multiple entry builds, which can be Main process, Preload scripts, Worker process, etc.
			// If you are familiar with Vite configuration, it will look really familiar.
			build: [
				{
					// `entry` is just an alias for `build.lib.entry` in the corresponding file of `config`.
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
		// Fuses are used to enable/disable various Electron functionality
		// at package time, before code signing the application
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
