import { apiClient } from "@/lib/api-client";
import type { User } from "@/types/api";

export const profileService = {
  getProfile(): Promise<User> {
    return apiClient.get<User>("/auth/me").then((r) => r.data);
  },
};
