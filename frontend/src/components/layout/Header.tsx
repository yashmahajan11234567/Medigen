import { CalendarDays, LogOut, ShieldCheck } from "lucide-react";
import { useLocation, useNavigate } from "react-router-dom";
import { Button } from "@/components/common/Button";
import { useAuth } from "@/hooks/useAuth";

const routeTitles: Record<string, { title: string; subtitle: string }> = {
  "/dashboard": {
    title: "Home Dashboard",
    subtitle: "Greeting, notifications, today's medicines, and inventory health at a glance.",
  },
  "/schedule": {
    title: "Medicine Scheduler",
    subtitle: "Structured reminders, bill-based creation, and adherence workflows.",
  },
  "/generic": {
    title: "Generic Finder",
    subtitle: "Deterministic exact composition matching with inventory handoff.",
  },
  "/inventory": {
    title: "Inventory Cabinet",
    subtitle: "Your medicine stock, expiry tracking, and scheduler synchronization.",
  },
  "/medical-records": {
    title: "Medical Records",
    subtitle: "Healthcare folders, document metadata, and module references.",
  },
};

export function Header() {
  const { pathname } = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const routeMeta =
    routeTitles[pathname] ?? routeTitles["/dashboard"];

  return (
    <header className="sticky top-0 z-20 rounded-t-[2rem] border-b border-slate-200/70 bg-white/90 px-4 py-4 backdrop-blur-sm sm:px-6 lg:px-8">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-brand-600">MediGen Workspace</p>
          <h1 className="mt-2 text-2xl font-semibold text-slate-900">
            {routeMeta.title}
          </h1>
          <p className="mt-1 max-w-2xl text-sm leading-6 text-slate-600">
            {routeMeta.subtitle}
          </p>
        </div>
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
          <div className="flex items-center gap-3 rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-mint-50 text-mint-700">
              <ShieldCheck className="h-5 w-5" />
            </div>
            <div>
              <p className="text-sm font-semibold text-slate-900">
                {user?.full_name ?? "Authenticated user"}
              </p>
              <p className="text-xs text-slate-500">{user?.email ?? "No email loaded"}</p>
            </div>
          </div>
          <div className="flex items-center gap-2 rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-600">
            <CalendarDays className="h-4 w-4 text-brand-500" />
            <span>{new Date().toLocaleDateString()}</span>
          </div>
          <Button
            variant="secondary"
            icon={<LogOut className="h-4 w-4" />}
            onClick={() => {
              logout();
              navigate("/login", { replace: true });
            }}
          >
            Sign out
          </Button>
        </div>
      </div>
    </header>
  );
}
