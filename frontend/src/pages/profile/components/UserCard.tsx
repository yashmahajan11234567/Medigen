import { Pencil } from "lucide-react";

export function UserCard() {
  return (
    <div className="rounded-3xl border border-slate-100 bg-white p-6 shadow-soft sm:p-8">
      <div className="flex flex-col items-center gap-4 sm:flex-row sm:gap-6">
        <div className="flex h-20 w-20 shrink-0 items-center justify-center rounded-3xl bg-gradient-to-br from-brand-100 to-mint-100 text-3xl font-bold text-brand-600 shadow-sm">
          <span>A</span>
        </div>
        <div className="min-w-0 flex-1 text-center sm:text-left">
          <h2 className="text-xl font-bold text-slate-900">Arjun Mehta</h2>
          <p className="mt-0.5 text-sm text-slate-500">arjun.mehta@email.com</p>
          <p className="text-sm text-slate-400">+91 98765 43210</p>
          <p className="mt-2 text-xs text-slate-400">
            Member since <span className="font-medium text-slate-600">January 2025</span>
          </p>
        </div>
        <button
          type="button"
          className="flex items-center gap-2 rounded-2xl border border-slate-200 bg-white px-5 py-2.5 text-sm font-semibold text-slate-700 shadow-soft transition hover:bg-slate-50 active:scale-[0.98]"
        >
          <Pencil className="h-4 w-4" />
          Edit Profile
        </button>
      </div>
    </div>
  );
}