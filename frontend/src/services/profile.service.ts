import { apiClient } from "@/lib/api-client";
import type { User } from "@/types/api";

export const profileService = {
  getProfile(): Promise<User> {
    return apiClient.get<User>("/users/me").then((r) => r.data);
  },

  updateProfile(payload: Partial<Pick<User, "full_name" | "email">>): Promise<User> {
    return apiClient.put<User>("/users/me", payload).then((r) => r.data);
  },
};