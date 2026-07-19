import { ArrowUpDown } from "lucide-react";

const sortOptions = ["Disease", "Hospital", "Date"];

interface SortDropdownProps {
  value: string;
  onChange: (value: string) => void;
}

export function SortDropdown({ value, onChange }: SortDropdownProps) {
  return (
    <div className="relative">
      <ArrowUpDown className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full appearance-none rounded-2xl border border-slate-200 bg-white py-3 pl-11 pr-10 text-sm font-medium text-slate-700 shadow-soft transition focus:border-brand-300 focus:outline-none focus:ring-4 focus:ring-brand-100"
        aria-label="Sort by"
      >
        {sortOptions.map((opt) => (
          <option key={opt} value={opt}>
            Sort by {opt}
          </option>
        ))}
      </select>
      <div className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2">
        <svg
          className="h-4 w-4 text-slate-400"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </div>
    </div>
  );
}