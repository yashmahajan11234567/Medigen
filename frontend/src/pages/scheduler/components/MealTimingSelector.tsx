import { cn } from "@/lib/cn";

const timings = ["Before Meal", "After Meal", "With Meal", "Anytime"];

interface MealTimingSelectorProps {
  value: string;
  onChange: (value: string) => void;
}

export function MealTimingSelector({ value, onChange }: MealTimingSelectorProps) {
  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
      {timings.map((t) => (
        <button
          key={t}
          type="button"
          onClick={() => onChange(t)}
          className={cn(
            "rounded-2xl border px-4 py-3 text-center text-sm font-medium transition",
            value === t
              ? "border-brand-200 bg-brand-50 text-brand-700 shadow-sm"
              : "border-slate-100 bg-white text-slate-600 hover:border-slate-200 hover:bg-slate-50",
          )}
        >
          {t}
        </button>
      ))}
    </div>
  );
}