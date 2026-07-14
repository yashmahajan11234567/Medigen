import { useEffect, useState } from "react";
import { ApiError, apiClient } from "@/lib/api-client";
import type { DashboardResponse } from "@/types/api";

interface UseDashboardResult {
  dashboard: DashboardResponse | null;
  isLoading: boolean;
  error: string | null;
  refresh: () => void;
}

export function useDashboard(): UseDashboardResult {
  const [dashboard, setDashboard] = useState<DashboardResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    let isActive = true;

    async function loadDashboard() {
      setIsLoading(true);
      setError(null);

      try {
        const response = await apiClient.get<DashboardResponse>("/dashboard");
        if (!isActive) {
          return;
        }
        setDashboard(response.data);
      } catch (caughtError) {
        if (!isActive) {
          return;
        }
        setError(
          caughtError instanceof ApiError
            ? caughtError.message
            : "We could not load your dashboard right now.",
        );
      } finally {
        if (isActive) {
          setIsLoading(false);
        }
      }
    }

    void loadDashboard();

    return () => {
      isActive = false;
    };
  }, [reloadKey]);

  return {
    dashboard,
    isLoading,
    error,
    refresh: () => setReloadKey((current) => current + 1),
  };
}
