import { apiClient } from "@/lib/api-client";
import type { LoginRequest, RegisterRequest, TokenResponse, User } from "@/types/api";

export const authService = {
  login(payload: LoginRequest): Promise<TokenResponse> {
    return apiClient.post<TokenResponse>("/auth/login", payload).then((r) => r.data);
  },

  register(payload: RegisterRequest): Promise<void> {
    return apiClient.post<void>("/auth/register", payload).then(() => undefined);
  },

  /** Fetch current user info (used by AuthContext for silent validation) */
  me(): Promise<User> {
    return apiClient.get<User>("/auth/me").then((r) => r.data);
  },
};