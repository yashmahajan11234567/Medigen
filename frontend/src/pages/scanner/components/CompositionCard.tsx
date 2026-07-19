import { Beaker } from "lucide-react";
import { Card } from "@/components/common/Card";
import { SectionTitle } from "@/pages/dashboard/components/SectionTitle";

export function CompositionCard() {
  return (
    <Card className="p-5 sm:p-6">
      <SectionTitle>Parsed Composition</SectionTitle>
      <div className="mt-4 flex items-center gap-4 rounded-2xl border border-mint-100 bg-mint-50 p-4">
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-mint-100 text-mint-700">
          <Beaker className="h-5 w-5" />
        </div>
        <div>
          <p className="font-semibold text-slate-900">Paracetamol 650 mg</p>
          <p className="mt-0.5 text-sm text-slate-500">Oral tablet for fever &amp; pain relief</p>
        </div>
      </div>
    </Card>
  );
}