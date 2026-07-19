import { Scan } from "lucide-react";

export function ScannerHeader() {
  return (
    <div className="flex items-center gap-4">
      <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl bg-brand-100 text-brand-600">
        <Scan className="h-7 w-7" />
      </div>
      <div>
        <h1 className="text-xl font-semibold text-slate-900">Generic Medicine Scanner</h1>
        <p className="mt-0.5 text-sm text-slate-500">Find exact generic medicine substitutes safely.</p>
      </div>
    </div>
  );
}