import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  const backendPort = env.BACKEND_PORT || "8000";
  const frontendPort = Number(env.FRONTEND_PORT || "5173");

  return {
    plugins: [react()],
    server: {
      host: "0.0.0.0",
      port: frontendPort,
      allowedHosts: ["captive-preamble-glamorous.ngrok-free.dev", "localhost", "127.0.0.1"],
      proxy: {
        "/api": {
          target: `http://backend-api:${backendPort}`,
          changeOrigin: true
        }
      }
    }
  };
});
