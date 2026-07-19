import { useState } from "react";
import { cn } from "@/lib/cn";

const preferences = [
  { label: "Medicine Reminders", desc: "Get reminded about scheduled medicines" },
  { label: "Low Stock Alerts", desc: "Notify when inventory is running low" },
  { label: "Expiry Alerts", desc: "Warn about medicines nearing expiry" },
  { label: "OCR Auto Scan", desc: "Automatically scan medicine labels" },
];

interface ToggleProps {
  checked: boolean;
  onChange: (v: boolean) => void;
}

function Toggle({ checked, onChange }: ToggleProps) {
  return (
    <button
      type="button"
      role="switch"
      aria-checked={checked}
      onClick={() => onChange(!checked)}
      className={cn(
        "relative h-6 w-11 shrink-0 rounded-full transition",
        checked ? "bg-mint-500" : "bg-slate-200",
      )}
    >
      <span
        className={cn(
          "absolute left-0.5 top-0.5 h-5 w-5 rounded-full bg-white shadow-sm transition",
          checked ? "translate-x-5" : "translate-x-0",
        )}
      />
    </button>
  );
}

export function PreferenceToggle() {
  const [states, setStates] = useState([true, false, true, false]);

  const toggle = (i: number) => {
    setStates((prev) => {
      const next = [...prev];
      next[i] = !next[i];
      return next;
    });
  };

  return (
    <div className="rounded-3xl border border-slate-100 bg-white shadow-soft">
      <div className="border-b border-slate-100 px-5 py-4">
        <h3 className="text-base font-semibold text-slate-900">App Preferences</h3>
      </div>
      <div className="divide-y divide-slate-50 px-5">
        {preferences.map((p, i) => (
          <div key={p.label} className="flex items-center justify-between py-4">
            <div className="min-w-0 flex-1 pr-4">
              <p className="text-sm font-medium text-slate-900">{p.label}</p>
              <p className="mt-0.5 text-xs text-slate-500">{p.desc}</p>
            </div>
            <Toggle checked={states[i]} onChange={() => toggle(i)} />
          </div>
        ))}
      </div>
    </div>
  );
}