import { Navigate, Outlet } from "react-router-dom";
import { LoadingScreen } from "@/components/common/LoadingScreen";
import { useAuth } from "@/hooks/useAuth";

export function GuestRoute() {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return <LoadingScreen />;
  }

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return <Outlet />;
}