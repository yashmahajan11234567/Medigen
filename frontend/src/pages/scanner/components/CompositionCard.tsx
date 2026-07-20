import { Beaker, FileText, Receipt } from "lucide-react";
import { Card } from "@/components/common/Card";
import { SectionTitle } from "@/pages/dashboard/components/SectionTitle";
import type { CanonicalComposition, MedicineEntry } from "@/types/api";

type CompositionCardData =
  | { mode: "composition"; composition: CanonicalComposition }
  | { mode: "pharmacy-bill"; medicines: MedicineEntry[] }
  | { mode: "document"; documentType: string; patientName: string | null }
  | { mode: null };

interface CompositionCardProps {
  data: CompositionCardData;
}

export function CompositionCard({ data }: CompositionCardProps) {
  if (data.mode === null) {
    return (
      <Card className="p-5 sm:p-6">
        <SectionTitle>Parsed Data</SectionTitle>
        <div className="mt-4 flex items-center gap-4 rounded-2xl border border-slate-100 bg-slate-50 p-4">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-slate-100 text-slate-400">
            <Beaker className="h-5 w-5" />
          </div>
          <div>
            <p className="text-sm text-slate-500">No data yet — scan a medicine to begin</p>
          </div>
        </div>
      </Card>
    );
  }

  if (data.mode === "composition") {
    const c = data.composition;
    return (
      <Card className="p-5 sm:p-6">
        <SectionTitle>Parsed Composition</SectionTitle>
        <div className="mt-4 flex items-center gap-4 rounded-2xl border border-mint-100 bg-mint-50 p-4">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-mint-100 text-mint-700">
            <Beaker className="h-5 w-5" />
          </div>
          <div>
            <p className="font-semibold text-slate-900">
              {c.ingredient} {c.strength} {c.unit}
            </p>
            <p className="mt-0.5 text-sm text-slate-500">
              {c.dosage_form} &middot; {c.route}
            </p>
          </div>
        </div>
      </Card>
    );
  }

  if (data.mode === "pharmacy-bill") {
    const meds = data.medicines;
    return (
      <Card className="p-5 sm:p-6">
        <SectionTitle>Medicines ({meds.length})</SectionTitle>
        <div className="mt-4 space-y-2">
          {meds.map((m, i) => (
            <div
              key={i}
              className="flex items-center gap-3 rounded-xl border border-slate-100 bg-white p-3"
            >
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-brand-50 text-brand-600">
                <Receipt className="h-4 w-4" />
              </div>
              <div className="min-w-0 flex-1">
                <p className="text-sm font-medium text-slate-900">
                  {m.medicine_name}
                </p>
                <p className="text-xs text-slate-500">
                  {m.strength && m.dosage_unit
                    ? `${m.strength} ${m.dosage_unit}`
                    : "Strength N/A"}
                  {m.quantity != null && ` · Qty: ${m.quantity}`}
                </p>
              </div>
            </div>
          ))}
        </div>
      </Card>
    );
  }

  // document mode
  return (
    <Card className="p-5 sm:p-6">
      <SectionTitle>Document Info</SectionTitle>
      <div className="mt-4 flex items-center gap-4 rounded-2xl border border-violet-100 bg-violet-50 p-4">
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-violet-100 text-violet-700">
          <FileText className="h-5 w-5" />
        </div>
        <div>
          <p className="font-semibold capitalize text-slate-900">
            {data.documentType.replace(/_/g, " ")}
          </p>
          {data.patientName && (
            <p className="mt-0.5 text-sm text-slate-500">
              Patient: {data.patientName}
            </p>
          )}
        </div>
      </div>
    </Card>
  );
}