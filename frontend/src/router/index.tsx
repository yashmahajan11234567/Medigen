import { Navigate, createBrowserRouter } from "react-router-dom";
import { AppShell } from "@/layouts/AppShell";
import { DashboardPage } from "@/pages/app/DashboardPage";
import { FeaturePlaceholderPage } from "@/pages/app/FeaturePlaceholderPage";
import { GenericFinderPage } from "@/pages/generic/GenericFinderPage";
import { InventoryPage } from "@/pages/inventory/InventoryPage";
import { LoginPage } from "@/pages/auth/LoginPage";
import { RegisterPage } from "@/pages/auth/RegisterPage";
import { NotFoundPage } from "@/pages/system/NotFoundPage";
import { SchedulerPage } from "@/pages/scheduler/SchedulerPage";
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
            element: (
              <FeaturePlaceholderPage
                eyebrow="Page 5"
                title="Medical Records Frontend Placeholder"
                description="Medical Records CRUD, search, filters, and module linking are ready on the backend. The Google Drive-inspired frontend will be implemented in its own approved phase."
                apiHighlights={[
                  "GET /api/v1/medical-records",
                  "GET /api/v1/medical-records/search",
                  "GET /api/v1/medical-records/filter",
                  "POST /api/v1/medical-records/link",
                ]}
              />
            ),
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