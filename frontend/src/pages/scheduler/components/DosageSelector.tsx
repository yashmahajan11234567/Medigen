import { cn } from "@/lib/cn";

interface DosageSelectorProps {
  morning: number;
  afternoon: number;
  night: number;
  onChange: (slot: "morning" | "afternoon" | "night") => void;
}

const slots = [
  { key: "morning" as const, label: "Morning", time: "🌅" },
  { key: "afternoon" as const, label: "Afternoon", time: "☀️" },
  { key: "night" as const, label: "Night", time: "🌙" },
];

export function DosageSelector({ morning, afternoon, night, onChange }: DosageSelectorProps) {
  const values = { morning, afternoon, night };

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-3 gap-3">
        {slots.map((slot) => {
          const val = values[slot.key];
          return (
            <div key={slot.key} className="text-center">
              <p className="mb-2 text-sm font-medium text-slate-600">
                {slot.time} {slot.label}
              </p>
              <button
                type="button"
                onClick={() => onChange(slot.key)}
                className={cn(
                  "mx-auto flex h-14 w-14 items-center justify-center rounded-2xl text-2xl font-bold transition",
                  val === 1
                    ? "bg-brand-500 text-white shadow-md shadow-brand-200"
                    : "bg-slate-100 text-slate-400 hover:bg-slate-200",
                )}
              >
                {val}
              </button>
            </div>
          );
        })}
      </div>
      <div className="flex items-center justify-center gap-2 text-center">
        <span className="rounded-full bg-brand-50 px-4 py-1.5 text-sm font-medium text-brand-700">
          [{morning}] — [{afternoon}] — [{night}]
        </span>
      </div>
    </div>
  );
}