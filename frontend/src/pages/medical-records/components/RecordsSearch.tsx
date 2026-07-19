import { Search } from "lucide-react";

export function RecordsSearch() {
  return (
    <div className="relative">
      <Search className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
      <input
        type="text"
        placeholder="Search records..."
        className="w-full rounded-2xl border border-slate-200 bg-white py-3 pl-11 pr-4 text-sm text-slate-900 placeholder-slate-400 shadow-soft transition focus:border-brand-300 focus:outline-none focus:ring-4 focus:ring-brand-100"
      />
    </div>
  );
}