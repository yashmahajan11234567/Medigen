import { Bell, Moon, Globe, Shield, KeyRound, ChevronRight } from "lucide-react";

const settings = [
  { icon: Bell, label: "Notifications" },
  { icon: Moon, label: "Dark Mode" },
  { icon: Globe, label: "Language" },
  { icon: Shield, label: "Privacy" },
  { icon: KeyRound, label: "Security" },
];

export function SettingsSection() {
  return (
    <div className="rounded-3xl border border-slate-100 bg-white shadow-soft">
      <div className="border-b border-slate-100 px-5 py-4">
        <h3 className="text-base font-semibold text-slate-900">Account Settings</h3>
      </div>
      <div className="divide-y divide-slate-50">
        {settings.map((s) => (
          <button
            key={s.label}
            type="button"
            className="flex w-full items-center gap-4 px-5 py-4 text-left transition hover:bg-slate-50"
          >
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-slate-100 text-slate-500">
              <s.icon className="h-4 w-4" />
            </div>
            <span className="flex-1 text-sm font-medium text-slate-900">{s.label}</span>
            <ChevronRight className="h-4 w-4 text-slate-300" />
          </button>
        ))}
      </div>
    </div>
  );
}