import { ScanSearch } from "lucide-react";

export function EmptyResults() {
  return (
    <div className="flex flex-col items-center justify-center rounded-3xl border-2 border-dashed border-slate-200 bg-white/50 p-12 text-center">
      <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-brand-50 text-brand-400">
        <ScanSearch className="h-7 w-7" />
      </div>
      <p className="mt-4 text-sm font-medium text-slate-500">No generic matches yet.</p>
      <p className="mt-1 text-xs text-slate-400">Scan or enter a medicine to find substitutes</p>
    </div>
  );
}