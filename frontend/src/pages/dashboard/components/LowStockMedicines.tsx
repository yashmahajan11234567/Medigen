import { TriangleAlert } from "lucide-react";
import { Card } from "@/components/common/Card";
import { SectionTitle } from "@/pages/dashboard/components/SectionTitle";

interface LowStockMedicineItem {
  id: number;
  name: string;
  quantity: number | null;
  quantity_unit: string | null;
  expiry_date: string | null;
}

function getWarningLevel(remaining: number | null): "high" | "medium" | "low" {
  if (remaining === null || remaining === undefined) return "low";
  if (remaining <= 2) return "high";
  if (remaining <= 5) return "medium";
  return "low";
}

const warningConfig = {
  high: { bg: "bg-rose-50", text: "text-rose-700", label: "Critical" },
  medium: { bg: "bg-amber-50", text: "text-amber-700", label: "Low" },
  low: { bg: "bg-brand-50", text: "text-brand-700", label: "Running" },
};

export function LowStockMedicines({ lowStockList }: { lowStockList: LowStockMedicineItem[] }) {
  if (lowStockList.length === 0) return null;

  return (
    <Card className="p-5 sm:p-6">
      <SectionTitle>Low Stock Medicines</SectionTitle>

      <div className="mt-5 space-y-3">
        {lowStockList.map((item) => {
          const level = getWarningLevel(item.quantity);
          const w = warningConfig[level];
          return (
            <div
              key={item.id}
              className="flex items-center gap-4 rounded-2xl border border-slate-100 bg-white p-4 transition hover:shadow-sm"
            >
              <div className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl ${w.bg}`}>
                <TriangleAlert className={`h-5 w-5 ${w.text}`} />
              </div>
              <div className="min-w-0 flex-1">
                <p className="font-semibold text-slate-900">{item.name}</p>
                <p className="mt-0.5 text-sm text-slate-500">
                  {item.quantity ?? 0} {item.quantity_unit ?? "units"} left
                </p>
              </div>
              <span className={`rounded-full px-3 py-1 text-xs font-semibold ${w.bg} ${w.text}`}>
                {w.label}
              </span>
            </div>
          );
        })}
      </div>
    </Card>
  );
}