import {
  Archive,
  Clock3,
  LayoutDashboard,
  Pill,
  Search,
} from "lucide-react";
import { NavLink } from "react-router-dom";
import { cn } from "@/lib/cn";

const mobileItems = [
  { to: "/dashboard", label: "Home", icon: LayoutDashboard },
  { to: "/schedule", label: "Schedule", icon: Clock3 },
  { to: "/generic", label: "Generic", icon: Search },
  { to: "/inventory", label: "Inventory", icon: Pill },
  { to: "/medical-records", label: "Records", icon: Archive },
];

export function MobileNav() {
  return (
    <nav className="fixed inset-x-4 bottom-4 z-30 rounded-[1.75rem] border border-white/80 bg-white/95 p-2 shadow-soft lg:hidden">
      <div className="grid grid-cols-5 gap-1">
        {mobileItems.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              cn(
                "flex flex-col items-center justify-center gap-1 rounded-2xl px-2 py-3 text-[11px] font-semibold transition",
                isActive
                  ? "bg-brand-600 text-white"
                  : "text-slate-500 hover:bg-slate-50 hover:text-slate-900",
              )
            }
          >
            <Icon className="h-4 w-4" />
            <span>{label}</span>
          </NavLink>
        ))}
      </div>
    </nav>
  );
}
