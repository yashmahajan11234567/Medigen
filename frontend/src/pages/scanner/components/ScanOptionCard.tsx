import type { ComponentType } from "react";

interface ScanOptionCardProps {
  icon: ComponentType<{ className?: string }>;
  title: string;
  description: string;
  accent: "blue" | "green" | "amber" | "purple";
}

const accentMap = {
  blue: { bg: "bg-brand-50", text: "text-brand-600", border: "hover:border-brand-200" },
  green: { bg: "bg-mint-50", text: "text-mint-700", border: "hover:border-mint-200" },
  amber: { bg: "bg-amber-50", text: "text-amber-700", border: "hover:border-amber-200" },
  purple: { bg: "bg-violet-50", text: "text-violet-600", border: "hover:border-violet-200" },
};

export function ScanOptionCard({ icon: Icon, title, description, accent }: ScanOptionCardProps) {
  const a = accentMap[accent];

  return (
    <button
      type="button"
      className={`flex flex-col items-center gap-2.5 rounded-3xl border border-white/70 bg-white/90 p-5 text-left shadow-card backdrop-blur-sm transition ${a.border} hover:shadow-md sm:p-6`}
    >
      <div className={`flex h-12 w-12 items-center justify-center rounded-2xl ${a.bg} ${a.text} sm:h-14 sm:w-14`}>
        <Icon className="h-5 w-5 sm:h-6 sm:w-6" />
      </div>
      <div className="text-center">
        <p className="text-sm font-semibold text-slate-900 sm:text-base">{title}</p>
        <p className="mt-0.5 text-xs text-slate-500 sm:text-sm">{description}</p>
      </div>
    </button>
  );
}