import { LogOut } from "lucide-react";

export function LogoutButton() {
  return (
    <button
      type="button"
      className="flex w-full items-center justify-center gap-2 rounded-2xl bg-rose-500 py-3.5 text-base font-semibold text-white shadow-lg shadow-rose-200 transition hover:bg-rose-600 active:scale-[0.98]"
    >
      <LogOut className="h-5 w-5" />
      Logout
    </button>
  );
}