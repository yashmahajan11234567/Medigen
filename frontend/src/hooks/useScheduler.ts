import { useState, useEffect } from "react";
import { apiClient } from "@/lib/api-client";
import type {
  ScheduleListResponse,
  ScheduleResponse,
  ScheduleCreateRequest,
  ScheduleUpdateRequest,
  ScheduleDeleteResponse,
} from "@/types/api";

interface UseSchedulerResult {
  schedules: ScheduleResponse[];
  todaySchedule: ScheduleResponse[]; // assume today endpoint returns list
  loading: boolean;
  todayLoading: boolean;
  error: string | null;
  todayError: string | null;
  createSchedule: (payload: ScheduleCreateRequest) => Promise<void>;
  updateSchedule: (id: number, payload: ScheduleUpdateRequest) => Promise<void>;
  deleteSchedule: (id: number) => Promise<void>;
  completeReminder: (reminderId: number) => Promise<void>;
  fetchSchedules: () => Promise<void>;
  fetchTodaySchedule: () => Promise<void>;
}

export function useScheduler(): UseSchedulerResult {
  const [schedules, setSchedules] = useState<ScheduleResponse[]>([]);
  const [todaySchedule, setTodaySchedule] = useState<ScheduleResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [todayLoading, setTodayLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [todayError, setTodayError] = useState<string | null>(null);

  const fetchSchedules = async () => {
    setLoading(true);
    setError(null);
    try {
      const resp = await apiClient.get<ScheduleListResponse>("/schedule");
      setSchedules(resp.data.items);
    } catch (err: any) {
      setError(
        err.response?.data?.message || err.message || "Failed to load schedules"
      );
      console.error("Schedule fetch error:", err);
    } finally {
      setLoading(false);
    }
  };

  const fetchTodaySchedule = async () => {
    setTodayLoading(true);
    setTodayError(null);
    try {
      const resp = await apiClient.get<ScheduleListResponse>("/schedule/today");
      setTodaySchedule(resp.data.items);
    } catch (err: any) {
      setTodayError(
        err.response?.data?.message ||
          err.message ||
          "Failed to load today's schedule"
      );
      console.error("Today schedule fetch error:", err);
    } finally {
      setTodayLoading(false);
    }
  };

  const createSchedule = async (
    payload: ScheduleCreateRequest
  ): Promise<void> => {
    setLoading(true);
    setError(null);
    try {
      await apiClient.post<ScheduleResponse>("/schedule", payload);
      // after creation, refresh list
      await fetchSchedules();
    } catch (err: any) {
      setError(
        err.response?.data?.message ||
          err.message ||
          "Failed to create schedule"
      );
      console.error("Schedule create error:", err);
    } finally {
      setLoading(false);
    }
  };

  const updateSchedule = async (
    id: number,
    payload: ScheduleUpdateRequest
  ): Promise<void> => {
    setLoading(true);
    setError(null);
    try {
      await apiClient.put<ScheduleResponse>(`/schedule/${id}`, payload);
      await fetchSchedules();
    } catch (err: any) {
      setError(
        err.response?.data?.message ||
          err.message ||
          `Failed to update schedule ${id}`
      );
      console.error("Schedule update error:", err);
    } finally {
      setLoading(false);
    }
  };

  const deleteSchedule = async (id: number): Promise<void> => {
    setLoading(true);
    setError(null);
    try {
      await apiClient.delete<ScheduleDeleteResponse>(`/schedule/${id}`);
      await fetchSchedules();
    } catch (err: any) {
      setError(
        err.response?.data?.message ||
          err.message ||
          `Failed to delete schedule ${id}`
      );
      console.error("Schedule delete error:", err);
    } finally {
      setLoading(false);
    }
  };

  const completeReminder = async (
    reminderId: number
  ): Promise<void> => {
    // assuming we don't need separate loading state for this action
    try {
      await apiClient.post<{ message: string }>(
        "/schedule/complete",
        { reminder_id: reminderId }
      );
      // after completing, refresh today schedule and possibly schedules (if completion affects status)
      await fetchTodaySchedule();
      await fetchSchedules();
    } catch (err: any) {
      setError(
        err.response?.data?.message ||
          err.message ||
          `Failed to complete reminder ${reminderId}`
      );
      console.error("Complete reminder error:", err);
    }
  };

  // initial load
  useEffect(() => {
    fetchSchedules();
    fetchTodaySchedule();
  }, []);

  return {
    schedules,
    todaySchedule,
    loading,
    todayLoading,
    error,
    todayError,
    createSchedule,
    updateSchedule,
    deleteSchedule,
    completeReminder,
    fetchSchedules,
    fetchTodaySchedule,
  };
}
