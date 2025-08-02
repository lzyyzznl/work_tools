import { App } from "vue";
import VXETable from "vxe-table";
import "vxe-table/lib/style.css";
import "vxe-pc-ui/lib/style.css";

// 导入 vxe-pc-ui 组件
import { VxeModal as VXEModal } from "vxe-pc-ui";
import { VxeButton as VXEButton } from "vxe-pc-ui";
import { VxeInput as VXEInput } from "vxe-pc-ui";
import { VxeCheckbox as VXECheckbox } from "vxe-pc-ui";
import { VxeSelect as VXESelect } from "vxe-pc-ui";

export function setupVxeTable(app: App) {
	app.use(VXETable);

	// 安装导出功能所需的组件
	app.use(VXEModal);
	app.use(VXEButton);
	app.use(VXEInput);
	app.use(VXECheckbox);
	app.use(VXESelect);
}
