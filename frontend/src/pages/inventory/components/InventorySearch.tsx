import { Search } from "lucide-react";

export function InventorySearch() {
  return (
    <div className="relative">
      <Search className="pointer-events-none absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-400" />
      <input
        type="text"
        placeholder="Search medicines..."
        className="w-full rounded-2xl border border-slate-200 bg-white py-3.5 pl-12 pr-4 text-sm text-slate-900 placeholder-slate-400 shadow-soft transition focus:border-brand-300 focus:outline-none focus:ring-4 focus:ring-brand-100"
      />
    </div>
  );
}