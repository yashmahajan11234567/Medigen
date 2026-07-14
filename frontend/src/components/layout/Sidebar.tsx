import {
  Archive,
  Clock3,
  LayoutDashboard,
  Pill,
  Search,
} from "lucide-react";
import { Card } from "@/components/common/Card";
import { Logo } from "@/components/layout/Logo";
import { NavItem } from "@/components/navigation/NavItem";

const navigationItems = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/schedule", label: "Scheduler", icon: Clock3 },
  { to: "/generic", label: "Generic Finder", icon: Search },
  { to: "/inventory", label: "Inventory", icon: Pill },
  { to: "/medical-records", label: "Medical Records", icon: Archive },
];

export function Sidebar() {
  return (
    <Card className="sticky top-4 hidden h-[calc(100vh-2rem)] w-[280px] shrink-0 overflow-hidden p-5 lg:flex lg:flex-col">
      <Logo />
      <div className="mt-8">
        <p className="px-4 text-xs font-semibold uppercase tracking-[0.24em] text-slate-400">
          Workspace
        </p>
        <nav className="mt-4 flex flex-col gap-2">
          {navigationItems.map((item) => (
            <NavItem key={item.to} {...item} />
          ))}
        </nav>
      </div>
      <div className="mt-auto rounded-3xl bg-brand-50 p-4 text-sm text-slate-600">
        <p className="font-semibold text-brand-700">Care at a glance</p>
        <p className="mt-2 leading-6">
          Your dashboard, schedule, inventory, and records all live inside one
          consistent MediGen workspace.
        </p>
      </div>
    </Card>
  );
}
