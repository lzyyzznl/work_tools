import { App } from "vue";
import VXETable from "vxe-table";
import "vxe-table/lib/style.css";
import "vxe-pc-ui/lib/style.css";

// 导入 vxe-pc-ui 组件
import VXEModal from "vxe-pc-ui/lib/modal";
import VXEButton from "vxe-pc-ui/lib/button";
import VXEInput from "vxe-pc-ui/lib/input";
import VXECheckbox from "vxe-pc-ui/lib/checkbox";
import VXESelect from "vxe-pc-ui/lib/select";

export function setupVxeTable(app: App) {
	app.use(VXETable);

	// 安装导出功能所需的组件
	app.use(VXEModal);
	app.use(VXEButton);
	app.use(VXEInput);
	app.use(VXECheckbox);
	app.use(VXESelect);
}
