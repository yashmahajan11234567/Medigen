import { cn } from "@/lib/cn";

export interface MedicineItem {
  id: number;
  name: string;
  genericName: string;
  brandName: string;
  type: "tablet" | "capsule" | "syrup" | "cream" | "injection" | "ointment" | "drops" | "inhaler" | "other";
  quantity: number | null;
  quantityUnit: string | null;
  expiryDate: string | null;
  purchaseDate: string | null;
  imagePath: string | null;
  notes: string | null;
  status: "healthy" | "low" | "expiring" | "expired";
  storageInstructions: string;
}

export function MedicineCard({ medicine, onClick }: { medicine: MedicineItem; onClick: (m: MedicineItem) => void }) {
  const statusConfig = {
    healthy: { label: "Healthy", dot: "bg-mint-500", bg: "bg-mint-50", text: "text-mint-700" },
    low: { label: "Low Stock", dot: "bg-amber-500", bg: "bg-amber-50", text: "text-amber-700" },
    expiring: { label: "Expiring Soon", dot: "bg-amber-500", bg: "bg-amber-50", text: "text-amber-700" },
    expired: { label: "Expired", dot: "bg-rose-500", bg: "bg-rose-50", text: "text-rose-700" },
  };

  const s = statusConfig[medicine.status];

  return (
    <button
      type="button"
      onClick={() => onClick(medicine)}
      className="group w-full rounded-2xl border border-slate-100 bg-white p-4 text-left shadow-soft hover:-translate-y-0.5 hover:shadow-md"
    >
      <div className="mb-3 flex h-24 items-center justify-center rounded-xl bg-gradient-to-br from-brand-50 to-mint-50">
        <span className="text-4xl opacity-60">💊</span>
      </div>
      <p className="font-semibold text-slate-900">{medicine.name}</p>
      <p className="mt-0.5 text-xs capitalize text-slate-400">{medicine.type}</p>
      <div className="mt-3 flex items-center justify-between">
        <span className="text-sm font-medium text-slate-700">
          {medicine.quantity} {medicine.quantityUnit}
        </span>
        <span className={cn("rounded-full px-2.5 py-0.5 text-xs font-semibold", s.bg, s.text)}>
          {s.label}
        </span>
      </div>
      <p className="mt-1 text-xs text-slate-400">Exp: {medicine.expiryDate}</p>
    </button>
  );
}

export function MedicineGrid({
  medicines,
  onSelect,
}: {
  medicines: MedicineItem[];
  onSelect: (m: MedicineItem) => void;
}) {
  return (
    <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 xl:grid-cols-4">
      {medicines.map((m) => (
        <MedicineCard key={m.id} medicine={m} onClick={onSelect} />
      ))}
    </div>
  );
}