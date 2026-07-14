function readEnv(name: string, fallback: string) {
  const value = import.meta.env[name];
  return typeof value === "string" && value.trim() ? value.trim() : fallback;
}

export const appConfig = {
  appName: readEnv("VITE_APP_NAME", "MediGen"),
  apiBaseUrl: readEnv("VITE_API_BASE_URL", "http://127.0.0.1:8000/api/v1"),
} as const;
