import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  return {
    plugins: [react()],
    server: {
      // Proxy tylko w trybie developerskim i tylko gdy zmienna jest ustawiona
      proxy: env.DEV_PROXY_TARGET
        ? { "/api": { target: env.DEV_PROXY_TARGET, changeOrigin: true } }
        : undefined,
    },
  };
});
