import { forwardRef } from "react";
import { cn } from "@/lib/cn";
import { Select as ChakraSelect } from "@chakra-ui/react";

interface SelectProps {
  className?: string;
  id?: string;
  label?: string;
  error?: string | null;
  hint?: string;
  options: { value: string; label: string }[];
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  isDisabled?: boolean;
}

export const Select = forwardRef<HTMLDivElement, SelectProps>(
  ({
    className,
    label,
    error,
    hint,
    id,
    options,
    value,
    onChange,
    placeholder = "Select an option",
    isDisabled = false,
    ...props
  }, ref) => {
    const fieldId =
      id ??
      (label
        ? label.toLowerCase().replace(/\s+/g, "-")
        : `select-${Math.random().toString(36).substr(2, 9)}`);

    return (
      <>
        {label && (
          <label htmlFor={fieldId} className="flex flex-col gap-2 text-sm text-slate-700">
            <span className="font-medium">{label}</span>
          </label>
        )}
        <div
          ref={ref}
          id={fieldId}
          className={cn(
            "relative",
            className,
          )}
        >
          <ChakraSelect
            value={value}
            onChange={(e) => onChange(e.target.value)}
            placeholder={placeholder}
            isDisabled={isDisabled}
            isInvalid={!!error}
            className={cn(
              "h-12 w-full rounded-2xl border border-slate-200 bg-white px-4 text-slate-900 outline-none transition focus:border-brand-300 focus:ring-4 focus:ring-brand-100",
              error ? "border-rose-300 focus:border-rose-300 focus:ring-rose-100" : "",
            )}
            {...props}
          >
            {/* Placeholder option */}
            {placeholder && (
              <option value="" disabled hidden>
                {placeholder}
              </option>
            )}
            {options.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </ChakraSelect>
        </div>
        {error ? <span className="text-xs text-rose-600">{error}</span> : null}
        {!error && hint ? <span className="text-xs text-slate-500">{hint}</span> : null}
      </>
    );
  },
);

Select.displayName = "Select";
