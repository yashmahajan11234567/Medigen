import { Card } from "@/components/common/Card";
import { SectionTitle } from "@/pages/dashboard/components/SectionTitle";

const dummyOCRText = `Paracetamol Tablets IP
650 mg

Batch: ABC123
MFG: Jan 2026
EXP: Dec 2028

Manufacturer: XYZ Pharma
M.R.P.: Rs. 35.00
`;

export function OCRPreviewCard() {
  return (
    <Card className="p-5 sm:p-6">
      <SectionTitle>Extracted Text</SectionTitle>
      <div className="mt-4 max-h-40 overflow-y-auto rounded-2xl bg-slate-50 p-4 font-mono text-sm leading-relaxed text-slate-700">
        <pre className="whitespace-pre-wrap">{dummyOCRText}</pre>
      </div>
      <div className="mt-3 flex items-center gap-2">
        <span className="h-2 w-2 rounded-full bg-mint-500" />
        <span className="text-xs text-slate-500">OCR confidence: 96.2%</span>
      </div>
    </Card>
  );
}