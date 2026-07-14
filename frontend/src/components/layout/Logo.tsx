import { HeartPulse } from "lucide-react";
import { appConfig } from "@/lib/app-config";

export function Logo() {
  return (
    <div className="flex items-center gap-3">
      <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-brand-600 to-mint-500 text-white shadow-soft">
        <HeartPulse className="h-6 w-6" />
      </div>
      <div>
        <p className="text-lg font-semibold text-slate-900">{appConfig.appName}</p>
        <p className="text-xs uppercase tracking-[0.24em] text-slate-500">
          Care Companion
        </p>
      </div>
    </div>
  );
}
