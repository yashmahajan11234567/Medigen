import { cn } from "@/lib/cn";

const durations = ["3 Days", "5 Days", "7 Days", "10 Days", "15 Days", "30 Days", "90 Days"];

interface DurationPickerProps {
  value: string;
  onChange: (value: string) => void;
}

export function DurationPicker({ value, onChange }: DurationPickerProps) {
  return (
    <div className="grid grid-cols-4 gap-2 sm:grid-cols-7">
      {durations.map((d) => (
        <button
          key={d}
          type="button"
          onClick={() => onChange(d)}
          className={cn(
            "rounded-xl border px-3 py-2.5 text-center text-sm font-medium transition",
            value === d
              ? "border-brand-200 bg-brand-50 text-brand-700"
              : "border-slate-100 bg-white text-slate-600 hover:border-slate-200 hover:bg-slate-50",
          )}
        >
          {d}
        </button>
      ))}
    </div>
  );
}