import { Bell, User } from "lucide-react";

interface DashboardHeaderProps {
  name: string;
}

export function DashboardHeader({ name }: DashboardHeaderProps) {
  const hour = new Date().getHours();
  let greeting: string;
  if (hour < 12) greeting = "Good Morning";
  else if (hour < 17) greeting = "Good Afternoon";
  else greeting = "Good Evening";

  return (
    <div className="flex items-center justify-between">
      <div className="flex items-center gap-4">
        <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-mint-100 text-mint-700">
          <User className="h-7 w-7" />
        </div>
        <div>
          <p className="text-sm font-medium text-slate-500">{greeting}</p>
          <h1 className="text-xl font-semibold text-slate-900">{name}</h1>
        </div>
      </div>
      <button
        type="button"
        className="relative flex h-12 w-12 items-center justify-center rounded-2xl bg-white shadow-soft transition hover:bg-slate-50"
      >
        <Bell className="h-5 w-5 text-slate-600" />
        <span className="absolute right-2.5 top-2.5 h-2.5 w-2.5 rounded-full bg-rose-500 ring-2 ring-white" />
      </button>
    </div>
  );
}