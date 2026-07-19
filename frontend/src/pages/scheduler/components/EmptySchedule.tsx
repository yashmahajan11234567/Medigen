import { CalendarX } from "lucide-react";

export function EmptySchedule() {
  return (
    <div className="flex flex-col items-center justify-center rounded-3xl border-2 border-dashed border-slate-200 bg-white/50 p-12 text-center">
      <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-slate-100 text-slate-400">
        <CalendarX className="h-7 w-7" />
      </div>
      <p className="mt-4 text-sm font-medium text-slate-500">No scheduled medicines.</p>
      <p className="mt-1 text-xs text-slate-400">Add a schedule using the form above</p>
    </div>
  );
}