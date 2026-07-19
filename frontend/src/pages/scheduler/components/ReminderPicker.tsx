import { Clock } from "lucide-react";

interface ReminderPickerProps {
  value: string;
  onChange: (value: string) => void;
}

export function ReminderPicker({ value, onChange }: ReminderPickerProps) {
  return (
    <div className="relative">
      <Clock className="pointer-events-none absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-400" />
      <input
        type="time"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full rounded-2xl border border-slate-200 bg-white py-3.5 pl-12 pr-4 text-sm text-slate-900 shadow-soft transition focus:border-brand-300 focus:outline-none focus:ring-4 focus:ring-brand-100"
      />
    </div>
  );
}