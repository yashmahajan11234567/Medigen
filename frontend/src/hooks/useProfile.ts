import { useState, useEffect } from "react";
import { apiClient } from "@/lib/api-client";
import type { User } from "@/types/api";

export function useProfile() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchProfile = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiClient.get<User>("/api/v1/users/me");
      setUser(response.data);
    } catch (err: any) {
      const message =
        err.response?.data?.message ||
        err.message ||
        "Failed to fetch profile";
      setError(message);
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProfile();
  }, []);

  // Return the state and a refetch function
  return {
    user,
    loading,
    error,
    refetch: fetchProfile,
  };
}