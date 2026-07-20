import { Card } from "@/components/common/Card";
import { SectionTitle } from "@/pages/dashboard/components/SectionTitle";
import { QualityBadge } from "@/pages/scanner/components/QualityBadge";
import type { ScanQualityDiagnostics } from "@/types/api";

interface OCRPreviewCardProps {
  extractedText: string;
  ocrConfidence: number | null;
  qualityDiagnostics: ScanQualityDiagnostics | null;
  processingTimeMs: number;
}

export function OCRPreviewCard({
  extractedText,
  ocrConfidence,
  qualityDiagnostics,
  processingTimeMs,
}: OCRPreviewCardProps) {
  return (
    <Card className="p-5 sm:p-6">
      <SectionTitle>Extracted Text</SectionTitle>
      <div className="mt-4 max-h-40 overflow-y-auto rounded-2xl bg-slate-50 p-4 font-mono text-sm leading-relaxed text-slate-700">
        <pre className="whitespace-pre-wrap">{extractedText}</pre>
      </div>

      <div className="mt-3 flex flex-wrap items-center gap-3">
        {/* OCR confidence */}
        <div className="flex items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-mint-500" />
          <span className="text-xs text-slate-500">
            OCR confidence:{" "}
            {ocrConfidence != null
              ? `${(ocrConfidence * 100).toFixed(1)}%`
              : "N/A"}
          </span>
        </div>

        {/* Processing time */}
        {processingTimeMs > 0 && (
          <span className="text-xs text-slate-400">
            ({processingTimeMs}ms)
          </span>
        )}

        {/* Quality indicator */}
        <QualityBadge diagnostics={qualityDiagnostics} />
      </div>
    </Card>
  );
}