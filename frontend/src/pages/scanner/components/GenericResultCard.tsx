import { BadgeCheck } from "lucide-react";

interface GenericResultCardProps {
  name: string;
  composition: string;
  strength: string;
  manufacturer: string;
  available: boolean;
}

export function GenericResultCard({ name, composition, strength, manufacturer, available }: GenericResultCardProps) {
  return (
    <div className="rounded-2xl border border-slate-100 bg-white p-4 transition hover:shadow-sm sm:p-5">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <p className="font-semibold text-slate-900">{name}</p>
            <span className="inline-flex items-center gap-1 rounded-full bg-mint-50 px-2.5 py-0.5 text-xs font-semibold text-mint-700">
              <BadgeCheck className="h-3 w-3" />
              Exact Match
            </span>
          </div>
          <p className="mt-1 text-sm text-slate-500">{composition}</p>
        </div>
        <span
          className={`shrink-0 rounded-full px-3 py-1 text-xs font-semibold ${
            available ? "bg-mint-50 text-mint-700" : "bg-rose-50 text-rose-700"
          }`}
        >
          {available ? "In Stock" : "Out of Stock"}
        </span>
      </div>
      <div className="mt-3 flex flex-wrap gap-x-6 gap-y-1 text-xs text-slate-400">
        <span>Strength: {strength}</span>
        <span>By: {manufacturer}</span>
      </div>
    </div>
  );
}