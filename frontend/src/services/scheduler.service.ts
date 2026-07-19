import { apiClient } from "@/lib/api-client";
import type {
  ScheduleCreateRequest,
  ScheduleDeleteResponse,
  ScheduleListResponse,
  ScheduleResponse,
  ScheduleUpdateRequest,
} from "@/types/api";

export const schedulerService = {
  getAll(): Promise<ScheduleListResponse> {
    return apiClient.get<ScheduleListResponse>("/schedule").then((r) => r.data);
  },

  getToday(): Promise<ScheduleListResponse> {
    return apiClient.get<ScheduleListResponse>("/schedule/today").then((r) => r.data);
  },

  getById(id: number): Promise<ScheduleResponse> {
    return apiClient.get<ScheduleResponse>(`/schedule/${id}`).then((r) => r.data);
  },

  create(payload: ScheduleCreateRequest): Promise<ScheduleResponse> {
    return apiClient.post<ScheduleResponse>("/schedule", payload).then((r) => r.data);
  },

  update(id: number, payload: ScheduleUpdateRequest): Promise<ScheduleResponse> {
    return apiClient.put<ScheduleResponse>(`/schedule/${id}`, payload).then((r) => r.data);
  },

  delete(id: number): Promise<ScheduleDeleteResponse> {
    return apiClient.delete<ScheduleDeleteResponse>(`/schedule/${id}`).then((r) => r.data);
  },

  completeReminder(payload: { reminder_id: number }): Promise<{ message: string }> {
    return apiClient.post<{ message: string }>("/schedule/complete", payload).then((r) => r.data);
  },
};