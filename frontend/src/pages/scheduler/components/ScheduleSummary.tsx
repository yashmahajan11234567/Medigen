import { Card } from "@/components/common/Card";

interface StatItem {
  label: string;
  value: number | string;
  accent: string;
}

const stats: StatItem[] = [
  { label: "Medicines Today", value: 5, accent: "bg-brand-500" },
  { label: "Completed", value: 1, accent: "bg-mint-500" },
  { label: "Remaining", value: 4, accent: "bg-amber-500" },
];

export function ScheduleSummary() {
  return (
    <div className="grid grid-cols-3 gap-3">
      {stats.map((s) => (
        <Card key={s.label} className="p-4 text-center">
          <p className="text-2xl font-bold text-slate-900">{s.value}</p>
          <p className="mt-1 text-xs text-slate-500">{s.label}</p>
          <div className={`mx-auto mt-2 h-1 w-8 rounded-full ${s.accent}`} />
        </Card>
      ))}
    </div>
  );
}