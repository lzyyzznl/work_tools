import { createApp } from "vue";
import { createPinia } from "pinia";
import App from "./App.vue";
import "uno.css";
import { setupVxeTable } from "./plugins/vxe-table";

const app = createApp(App);
const pinia = createPinia();

app.use(pinia);
setupVxeTable(app);
app.mount("#app");
