import type { ComponentType } from "react";
import { useNavigate } from "react-router-dom";

interface QuickActionCardProps {
  title: string;
  description: string;
  icon: ComponentType<{ className?: string }>;
  to: string;
  accent: "blue" | "green" | "amber" | "purple";
}

const accentMap = {
  blue: { bg: "bg-brand-50", text: "text-brand-600", border: "hover:border-brand-200" },
  green: { bg: "bg-mint-50", text: "text-mint-700", border: "hover:border-mint-200" },
  amber: { bg: "bg-amber-50", text: "text-amber-700", border: "hover:border-amber-200" },
  purple: { bg: "bg-violet-50", text: "text-violet-600", border: "hover:border-violet-200" },
};

export function QuickActionCard({ title, description, icon: Icon, to, accent }: QuickActionCardProps) {
  const navigate = useNavigate();
  const a = accentMap[accent];

  return (
    <button
      type="button"
      onClick={() => navigate(to)}
      className={`flex flex-col items-center gap-3 rounded-3xl border border-white/70 bg-white/90 p-6 text-left shadow-card backdrop-blur-sm transition ${a.border} hover:shadow-md`}
    >
      <div className={`flex h-14 w-14 items-center justify-center rounded-2xl ${a.bg} ${a.text}`}>
        <Icon className="h-6 w-6" />
      </div>
      <div className="text-center">
        <p className="font-semibold text-slate-900">{title}</p>
        <p className="mt-1 text-sm leading-5 text-slate-500">{description}</p>
      </div>
    </button>
  );
}