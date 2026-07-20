import { BadgeCheck, FlaskConical } from "lucide-react";
import type { GenericMedicineSummary } from "@/types/api";

const DOSAGE_FORM_LABELS: Record<string, string> = {
  tablet: "Tablet",
  capsule: "Capsule",
  syrup: "Syrup",
  cream: "Cream",
  injection: "Injection",
  ointment: "Ointment",
  drops: "Drops",
  inhaler: "Inhaler",
  other: "Other",
};

interface GenericResultCardProps {
  medicine: GenericMedicineSummary;
}

export function GenericResultCard({ medicine }: GenericResultCardProps) {
  const { name, generic_name, brand_name, composition } = medicine;
  const isGeneric = !!generic_name;

  return (
    <div className="rounded-2xl border border-slate-100 bg-white p-4 transition hover:shadow-sm sm:p-5">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <p className="font-semibold text-slate-900">{name}</p>
            <span className="inline-flex items-center gap-1 rounded-full bg-mint-50 px-2.5 py-0.5 text-xs font-semibold text-mint-700">
              <BadgeCheck className="h-3 w-3" />
              {isGeneric ? "Generic" : "Brand"}
            </span>
          </div>
          {generic_name && (
            <p className="mt-1 text-sm text-slate-500">{generic_name}</p>
          )}
          {brand_name && (
            <p className="mt-1 text-sm text-slate-500">Brand: {brand_name}</p>
          )}
        </div>

        {composition && (
          <span className="inline-flex shrink-0 items-center gap-1 rounded-full bg-brand-50 px-3 py-1 text-xs font-medium text-brand-700">
            <FlaskConical className="h-3 w-3" />
            {composition.ingredient} {composition.strength} {composition.unit}
          </span>
        )}
      </div>

      <div className="mt-3 flex flex-wrap gap-x-6 gap-y-1 text-xs text-slate-400">
        {composition?.dosage_form != null && (
          <span>
            Form:{" "}
            {DOSAGE_FORM_LABELS[composition.dosage_form] ?? composition.dosage_form}
          </span>
        )}
        {composition?.route && <span>Route: {composition.route}</span>}
      </div>
    </div>
  );
}