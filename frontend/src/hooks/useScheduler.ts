import { useState, useEffect } from "react";
import { schedulerService } from "@/services/scheduler.service";
import type { ScheduleResponse, ScheduleCreateRequest, ScheduleUpdateRequest } from "@/types/api";

export function useScheduler() {
  const [schedules, setSchedules] = useState<Array<ScheduleResponse>>([]);
  const [todaySchedules, setTodaySchedules] = useState<Array<ScheduleResponse>>([]);
  const [loading, setLoading] = useState<boolean>(true); // initial load
  const [refreshing, setRefreshing] = useState<boolean>(false); // manual refresh
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const fetchSchedules = async (isRefresh: boolean = false) => {
    if (!isRefresh) {
      setLoading(true);
      setError(null);
    }
    try {
      const response = await schedulerService.getAll();
      setSchedules(response.items);
    } catch (err: any) {
      const message =
        err.response?.data?.message ||
        err.message ||
        "Failed to fetch schedules";
      setError(message);
      setSchedules([]);
    } finally {
      if (!isRefresh) {
        setLoading(false);
      }
    }
  };

  const fetchTodaySchedules = async (isRefresh: boolean = false) => {
    if (!isRefresh) {
      setLoading(true);
      setError(null);
    }
    try {
      const response = await schedulerService.getToday();
      setTodaySchedules(response.items);
    } catch (err: any) {
      // Only set error if not refreshing to avoid overwriting the main error?
      // We'll set error only if it's the initial load.
      if (!isRefresh) {
        const message =
          err.response?.data?.message ||
          err.message ||
          "Failed to fetch today's schedule";
        setError(message);
      }
      setTodaySchedules([]);
    } finally {
      if (!isRefresh) {
        setLoading(false);
      }
    }
  };

  const createSchedule = async (payload: ScheduleCreateRequest) => {
    try {
      const response = await schedulerService.create(payload);
      await refresh(); // refetch both lists
      setSuccess("Schedule created.");
      return response;
    } catch (err: any) {
      const message =
        err.response?.data?.message ||
        err.message ||
        "Failed to create schedule";
      setError(message);
      throw err;
    }
  };

  const updateSchedule = async (id: number, payload: ScheduleUpdateRequest) => {
    try {
      const response = await schedulerService.update(id, payload);
      await refresh(); // refetch both lists
      setSuccess("Schedule updated.");
      return response;
    } catch (err: any) {
      const message =
        err.response?.data?.message ||
        err.message ||
        "Failed to update schedule";
      setError(message);
      throw err;
    }
  };

  const refresh = async () => {
    setRefreshing(true);
    setSuccess(null);
    setError(null);
    try {
      await Promise.all([
        fetchSchedules(true), // true indicates it's a refresh
        fetchTodaySchedules(true),
      ]);
      setSuccess("Schedule updated.");
    } catch (err: any) {
      const message =
        err.response?.data?.message ||
        err.message ||
        "Failed to refresh schedule";
      setError(message);
    } finally {
      setRefreshing(false);
    }
  };

  // Fetch on mount
  useEffect(() => {
    fetchSchedules();
    fetchTodaySchedules();
  }, []);

  return {
    schedules,
    todaySchedules,
    loading,
    refreshing,
    error,
    success,
    refresh,
    createSchedule,
    updateSchedule,
  };
}