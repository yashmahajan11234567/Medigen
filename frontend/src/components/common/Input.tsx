import { forwardRef, type InputHTMLAttributes } from "react";
import { cn } from "@/lib/cn";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
  error?: string | null;
  hint?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, label, error, hint, id, ...props }, ref) => {
    const fieldId = id ?? label.toLowerCase().replace(/\s+/g, "-");

    return (
      <label htmlFor={fieldId} className="flex flex-col gap-2 text-sm text-slate-700">
        <span className="font-medium">{label}</span>
        <input
          ref={ref}
          id={fieldId}
          className={cn(
            "h-12 rounded-2xl border border-slate-200 bg-white px-4 text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-brand-300 focus:ring-4 focus:ring-brand-100",
            error ? "border-rose-300 focus:border-rose-300 focus:ring-rose-100" : "",
            className,
          )}
          {...props}
        />
        {error ? <span className="text-xs text-rose-600">{error}</span> : null}
        {!error && hint ? <span className="text-xs text-slate-500">{hint}</span> : null}
      </label>
    );
  },
);

Input.displayName = "Input";
