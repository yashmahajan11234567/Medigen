import { Navigate, createBrowserRouter } from "react-router-dom";
import { AppShell } from "@/layouts/AppShell";
import { DashboardPage } from "@/pages/app/DashboardPage";
import { FeaturePlaceholderPage } from "@/pages/app/FeaturePlaceholderPage";
import { GenericFinderPage } from "@/pages/generic/GenericFinderPage";
import { LoginPage } from "@/pages/auth/LoginPage";
import { RegisterPage } from "@/pages/auth/RegisterPage";
import { NotFoundPage } from "@/pages/system/NotFoundPage";
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
            element: (
              <FeaturePlaceholderPage
                eyebrow="Page 2"
                title="Scheduler Frontend Placeholder"
                description="The Schedule backend is verified, including CRUD, today's reminders, bill-based creation, and completion flow. This page remains intentionally unimplemented in Phase 8.1."
                apiHighlights={[
                  "GET /api/v1/schedule",
                  "GET /api/v1/schedule/today",
                  "POST /api/v1/schedule/from-bill",
                  "POST /api/v1/schedule/complete",
                ]}
              />
            ),
          },
          {
            path: "/generic",
            element: <GenericFinderPage />,
          },
          {
            path: "/inventory",
            element: (
              <FeaturePlaceholderPage
                eyebrow="Page 4"
                title="Inventory Frontend Placeholder"
                description="Inventory CRUD, search, filters, and summary are all available on the backend. This route currently exists only to prove the shared layout and protected navigation."
                apiHighlights={[
                  "GET /api/v1/inventory",
                  "GET /api/v1/inventory/search",
                  "GET /api/v1/inventory/filter",
                  "GET /api/v1/inventory/summary",
                ]}
              />
            ),
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
