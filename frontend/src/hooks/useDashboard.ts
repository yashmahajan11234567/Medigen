import { useState, useEffect } from "react";
import { dashboardService } from "@/services/dashboard.service";
import type { DashboardResponse } from "@/types/api";

export function useDashboard() {
  const [dashboard, setDashboard] = useState<DashboardResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchDashboard = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await dashboardService.getSummary();
      setDashboard(response);
    } catch (err: any) {
      setError(
        err.response?.data?.message ||
          err.message ||
          "Failed to load dashboard"
      );
      setDashboard(null);
    } finally {
      setLoading(false);
    }
  };

  // Fetch on mount
  useEffect(() => {
    fetchDashboard();
  }, []);

  return {
    dashboard,
    loading,
    error,
    refetch: fetchDashboard,
  };
}