import { apiClient } from "@/lib/api-client";
import type { DashboardResponse } from "@/types/api";

export const dashboardService = {
  getSummary(): Promise<DashboardResponse> {
    return apiClient.get<DashboardResponse>("/dashboard").then((r) => r.data);
  },
};