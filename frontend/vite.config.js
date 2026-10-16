import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// `npm run dev` -> http://localhost:5173, with /api forwarded to the FastAPI server.
// `npm run build` -> dist/, which the API serves at http://localhost:8000/app/
export default defineConfig({
  plugins: [react()],
  base: "/app/",
  server: {
    proxy: { "/api": "http://localhost:8000" },
  },
});
