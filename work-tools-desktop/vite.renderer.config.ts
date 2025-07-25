import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import UnoCSS from "@unocss/vite";
import path from "path";

// https://vitejs.dev/config
export default defineConfig({
	plugins: [vue(), UnoCSS()],
	resolve: {
		alias: {
			"@": path.resolve(__dirname, "src"),
			"@/types": path.resolve(__dirname, "src/renderer/types"),
			"@/components": path.resolve(__dirname, "src/renderer/components"),
			"@/composables": path.resolve(__dirname, "src/renderer/composables"),
			"@/stores": path.resolve(__dirname, "src/renderer/stores"),
			"@/utils": path.resolve(__dirname, "src/renderer/utils"),
		},
	},
});
