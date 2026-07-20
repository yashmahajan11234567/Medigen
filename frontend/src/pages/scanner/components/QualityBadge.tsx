import { AlertTriangle, CheckCircle, Info } from "lucide-react";
import type { ScanQualityDiagnostics } from "@/types/api";

interface QualityBadgeProps {
  diagnostics: ScanQualityDiagnostics | null;
}

const ISSUE_LABELS: Record<string, { label: string; bg: string; text: string; dot: string }> = {
  blurry: { label: "Blurry", bg: "bg-amber-50", text: "text-amber-700", dot: "bg-amber-500" },
  too_dark: { label: "Too Dark", bg: "bg-amber-50", text: "text-amber-700", dot: "bg-amber-500" },
  overexposed: { label: "Overexposed", bg: "bg-amber-50", text: "text-amber-700", dot: "bg-amber-500" },
  low_contrast: { label: "Low Contrast", bg: "bg-amber-50", text: "text-amber-700", dot: "bg-amber-500" },
  corrupted: { label: "Corrupted", bg: "bg-rose-50", text: "text-rose-700", dot: "bg-rose-500" },
  empty: { label: "Empty", bg: "bg-rose-50", text: "text-rose-700", dot: "bg-rose-500" },
};

export function QualityBadge({ diagnostics }: QualityBadgeProps) {
  if (!diagnostics) {
    return (
      <span className="inline-flex items-center gap-1.5 rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-medium text-slate-400">
        <Info className="h-3 w-3" />
        No quality data
      </span>
    );
  }

  if (diagnostics.is_pass && diagnostics.issues.length === 0) {
    return (
      <span className="inline-flex items-center gap-1.5 rounded-full bg-mint-50 px-2.5 py-0.5 text-xs font-medium text-mint-700">
        <CheckCircle className="h-3 w-3" />
        Good Quality
      </span>
    );
  }

  return (
    <div className="flex flex-wrap items-center gap-1.5">
      {diagnostics.issues.map((issue) => {
        const meta = ISSUE_LABELS[issue.toLowerCase()] ?? {
          label: issue,
          bg: "bg-amber-50",
          text: "text-amber-700",
          dot: "bg-amber-500",
        };
        return (
          <span
            key={issue}
            className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium ${meta.bg} ${meta.text}`}
          >
            <AlertTriangle className="h-3 w-3" />
            {meta.label}
          </span>
        );
      })}
    </div>
  );
}