import { Pill, CalendarClock, ClipboardList, Package } from "lucide-react";

const stats = [
  { label: "Total Medicines", value: 24, icon: Pill, accent: "bg-brand-50 text-brand-600" },
  { label: "Active Schedules", value: 5, icon: CalendarClock, accent: "bg-mint-50 text-mint-700" },
  { label: "Medical Records", value: 12, icon: ClipboardList, accent: "bg-violet-50 text-violet-600" },
  { label: "Inventory Items", value: 18, icon: Package, accent: "bg-amber-50 text-amber-700" },
];

export function HealthSummary() {
  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
      {stats.map((s) => (
        <div
          key={s.label}
          className="rounded-3xl border border-slate-100 bg-white p-4 shadow-soft"
        >
          <div className={`flex h-10 w-10 items-center justify-center rounded-2xl ${s.accent}`}>
            <s.icon className="h-5 w-5" />
          </div>
          <p className="mt-3 text-xl font-bold text-slate-900">{s.value}</p>
          <p className="mt-0.5 text-xs text-slate-500">{s.label}</p>
        </div>
      ))}
    </div>
  );
}