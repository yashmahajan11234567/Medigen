import { Navigate, createBrowserRouter } from "react-router-dom";
import { AppShell } from "@/layouts/AppShell";
import { DashboardPage } from "@/pages/app/DashboardPage";
import { GenericFinderPage } from "@/pages/generic/GenericFinderPage";
import { InventoryPage } from "@/pages/inventory/InventoryPage";
import { LoginPage } from "@/pages/auth/LoginPage";
import { RegisterPage } from "@/pages/auth/RegisterPage";
import { NotFoundPage } from "@/pages/system/NotFoundPage";
import { SchedulerPage } from "@/pages/scheduler/SchedulerPage";
import { MedicalRecordsPage } from "@/pages/medical-records/MedicalRecordsPage";
import { GuestRoute } from "@/router/GuestRoute";
import { ProtectedRoute } from "@/router/ProtectedRoute";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <Navigate to="/dashboard" replace />,
  },
  {
    element: <GuestRoute />,
    children: [
      {
        path: "/login",
        element: <LoginPage />,
      },
      {
        path: "/register",
        element: <RegisterPage />,
      },
    ],
  },
  {
    element: <ProtectedRoute />,
    children: [
      {
        element: <AppShell />,
        children: [
          {
            path: "/dashboard",
            element: <DashboardPage />,
          },
          {
            path: "/schedule",
            element: <SchedulerPage />,
          },
          {
            path: "/generic",
            element: <GenericFinderPage />,
          },
          {
            path: "/inventory",
            element: <InventoryPage />,
          },
          {
            path: "/medical-records",
            element: <MedicalRecordsPage />,
          },
        ],
      },
    ],
  },
  {
    path: "*",
    element: <NotFoundPage />,
  },
]);