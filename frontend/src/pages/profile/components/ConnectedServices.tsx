import { Cloud, Database, Mail } from "lucide-react";

const services = [
  { icon: Cloud, label: "Google Drive", connected: true },
  { icon: Database, label: "Cloud Backup", connected: false },
  { icon: Mail, label: "Email Notifications", connected: true },
];

export function ConnectedServices() {
  return (
    <div className="rounded-3xl border border-slate-100 bg-white shadow-soft">
      <div className="border-b border-slate-100 px-5 py-4">
        <h3 className="text-base font-semibold text-slate-900">Connected Services</h3>
      </div>
      <div className="divide-y divide-slate-50">
        {services.map((s) => (
          <div key={s.label} className="flex items-center gap-4 px-5 py-4">
            <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-slate-100 text-slate-500">
              <s.icon className="h-5 w-5" />
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-sm font-medium text-slate-900">{s.label}</p>
            </div>
            <span
              className={`rounded-full px-3 py-1 text-[11px] font-semibold ${
                s.connected
                  ? "bg-mint-50 text-mint-700"
                  : "bg-slate-100 text-slate-500"
              }`}
            >
              {s.connected ? "Connected" : "Connect"}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}