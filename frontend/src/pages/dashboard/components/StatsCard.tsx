import type { ComponentType } from "react";
import { Card } from "@/components/common/Card";

interface StatsCardProps {
  title: string;
  value: number | string;
  icon: ComponentType<{ className?: string }>;
  accent: "blue" | "green" | "amber" | "purple";
}

const accentMap = {
  blue: { bg: "bg-brand-50", text: "text-brand-600" },
  green: { bg: "bg-mint-50", text: "text-mint-700" },
  amber: { bg: "bg-amber-50", text: "text-amber-700" },
  purple: { bg: "bg-violet-50", text: "text-violet-600" },
};

export function StatsCard({ title, value, icon: Icon, accent }: StatsCardProps) {
  const a = accentMap[accent];
  return (
    <Card className="flex items-center gap-4 p-5">
      <div className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl ${a.bg} ${a.text}`}>
        <Icon className="h-5 w-5" />
      </div>
      <div className="min-w-0">
        <p className="text-2xl font-bold text-slate-900">{value}</p>
        <p className="truncate text-sm text-slate-500">{title}</p>
      </div>
    </Card>
  );
}