import { app, BrowserWindow, ipcMain, Menu, dialog } from "electron";
import path from "node:path";
import started from "electron-squirrel-startup";
import * as fileSystem from "./fileSystem";

// Handle creating/removing shortcuts on Windows when installing/uninstalling.
if (started) {
	app.quit();
}

// Enable remote debugging for VS Code in development
if (process.env.NODE_ENV === "development") {
	app.commandLine.appendSwitch("remote-debugging-port", "9222");
}

const createWindow = () => {
	// Create the browser window.
	const mainWindow = new BrowserWindow({
		width: 1200,
		height: 800,
		minWidth: 1200,
		minHeight: 800,
		webPreferences: {
			preload: path.join(__dirname, "preload.js"),
			contextIsolation: true,
			nodeIntegration: false,
		},
		titleBarStyle: "default",
		show: false,
	});

	// Show window when ready to prevent visual flash
	mainWindow.once("ready-to-show", () => {
		mainWindow.show();
	});

	// and load the index.html of the app.
	if (MAIN_WINDOW_VITE_DEV_SERVER_URL) {
		mainWindow.loadURL(MAIN_WINDOW_VITE_DEV_SERVER_URL);
	} else {
		mainWindow.loadFile(
			path.join(__dirname, `../renderer/${MAIN_WINDOW_VITE_NAME}/index.html`)
		);
	}

	// Open the DevTools in development
	if (process.env.NODE_ENV === "development") {
		mainWindow.webContents.openDevTools();
	}
};

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.on("ready", () => {
	// 移除默认菜单栏
	Menu.setApplicationMenu(null);
	createWindow();
});

// Quit when all windows are closed, except on macOS. There, it's common
// for applications and their menu bar to stay active until the user quits
// explicitly with Cmd + Q.
app.on("window-all-closed", () => {
	if (process.platform !== "darwin") {
		app.quit();
	}
});

app.on("activate", () => {
	// On OS X it's common to re-create a window in the app when the
	// dock icon is clicked and there are no other windows open.
	if (BrowserWindow.getAllWindows().length === 0) {
		createWindow();
	}
});

// In this file you can include the rest of your app's specific main process
// code. You can also put them in separate files and import them here.

// 文件系统 IPC 处理器
ipcMain.handle("file-system:select-files", async (event, options) => {
	return await fileSystem.selectFiles(options);
});

ipcMain.handle("file-system:select-directory", async () => {
	return await fileSystem.selectDirectory();
});

ipcMain.handle("file-system:read-file", async (event, filePath) => {
	return await fileSystem.readFile(filePath);
});

ipcMain.handle("file-system:write-file", async (event, filePath, data) => {
	return await fileSystem.writeFile(filePath, data);
});

ipcMain.handle("file-system:rename-file", async (event, oldPath, newPath) => {
	return await fileSystem.renameFile(oldPath, newPath);
});

ipcMain.handle("file-system:check-file-exists", async (event, filePath) => {
	return await fileSystem.checkFileExists(filePath);
});

// 对话框 IPC 处理器
ipcMain.handle("dialog:show-save-dialog", async (event, options) => {
	const result = await dialog.showSaveDialog(options);
	return result;
});
