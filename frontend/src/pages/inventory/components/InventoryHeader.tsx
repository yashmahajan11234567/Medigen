import { Bell, Pill } from "lucide-react";

export function InventoryHeader() {
  return (
    <div className="flex items-center justify-between">
      <div className="flex items-center gap-4">
        <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl bg-mint-100 text-mint-700">
          <Pill className="h-7 w-7" />
        </div>
        <div>
          <h1 className="text-xl font-semibold text-slate-900">Inventory</h1>
          <p className="mt-0.5 text-sm text-slate-500">Manage your medicines easily.</p>
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