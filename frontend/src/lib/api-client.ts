import axios from "axios";
import { appConfig } from "@/lib/app-config";
import { AUTH_TOKEN_KEY } from "@/lib/storage";
import type { ApiErrorPayload } from "@/types/api";

export class ApiError extends Error {
  status?: number;
  code?: string;
  details?: Array<Record<string, unknown>>;

  constructor(message: string, options?: Partial<ApiError>) {
    super(message);
    this.name = "ApiError";
    Object.assign(this, options);
  }
}

export const apiClient = axios.create({
  baseURL: appConfig.apiBaseUrl,
  headers: {
    "Content-Type": "application/json",
  },
});

apiClient.interceptors.request.use((config) => {
  const token = window.localStorage.getItem(AUTH_TOKEN_KEY);
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const payload = error.response?.data as ApiErrorPayload | undefined;
    return Promise.reject(
      new ApiError(payload?.message ?? "We could not reach the MediGen API.", {
        status: error.response?.status,
        code: payload?.code,
        details: payload?.details,
      }),
    );
  },
);
