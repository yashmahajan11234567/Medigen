import { forwardRef, type ChangeEvent } from "react";
import { cn } from "@/lib/cn";

interface DatePickerProps {
  name?: string;
  className?: string;
  id?: string;
  label?: string;
  error?: string | null;
  hint?: string;
  value: string | null;
  onChange: (value: string | null) => void;
  placeholder?: string;
  isDisabled?: boolean;
  min?: string;
  max?: string;
}

export const DatePicker = forwardRef<HTMLDivElement, DatePickerProps>(
  ({
    className,
    label,
    error,
    hint,
    id,
    value,
    onChange,
    placeholder = "Select a date",
    isDisabled = false,
    min,
    max,
    ...props
  }, ref) => {
    const fieldId = id ?? ((label ?? "").toLowerCase().replace(/\s+/g, "-") || `date-${Math.random().toString(36).substr(2, 9)}`);

    const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
      onChange(e.target.value || null);
    };

    return (
      <label htmlFor={fieldId} className="flex flex-col gap-2 text-sm text-slate-700">
        <span className="font-medium">{label}</span>
        <div
          ref={ref}
          id={fieldId}
          className={cn(
            "relative",
            className,
          )}
        >
          <input
            type="date"
            value={value || ""}
            onChange={handleChange}
            placeholder={placeholder}
            disabled={isDisabled}
            min={min}
            max={max}
            className={cn(
              "h-12 w-full rounded-2xl border border-slate-200 bg-white px-4 text-slate-900 outline-none transition focus:border-brand-300 focus:ring-4 focus:ring-brand-100",
              error ? "border-rose-300 focus:border-rose-300 focus:ring-rose-100" : "",
            )}
            {...props}
          />
        </div>
        {error ? <span className="text-xs text-rose-600">{error}</span> : null}
        {!error && hint ? <span className="text-xs text-slate-500">{hint}</span> : null}
      </label>
    );
  },
);

DatePicker.displayName = "DatePicker";
