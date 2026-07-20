import { CheckCircle, XCircle, Clock } from "lucide-react";
import type { SubmissionResultItem } from "@/types/api";

interface SubmissionSummaryProps {
  /** Results of inventory submission */
  results: SubmissionResultItem[];
  /** Callback to navigate to inventory */
  onViewInventory: () => void;
  /** Callback to reset scanning */
  onScanAnother: () => void;
}

export default function SubmissionSummary({
  results,
  onViewInventory,
  onScanAnother,
}: SubmissionSummaryProps) {
  /* Count categories */
  const addedCount = results.filter(r => r.status === "added").length;
  const skippedCount = results.filter(r => r.status === "skipped").length;
  const failedCount = results.filter(r => r.status === "failed").length;

  const overallStatus = results.length === 0 ? "no-data" :
    addedCount > 0 && skippedCount === 0 && failedCount === 0 ? "success" :
    failedCount > 0 ? "failed" : "partial";

  /* Overall summary text */
  const summaryText = `${addedCount} added, ${skippedCount} skipped, ${failedCount} failed`;

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "success": return CheckCircle;
      case "failed": return XCircle;
      default: return Clock;
    }
  };

  const IconComponent = getStatusIcon(overallStatus);

  const statusColors: Record<string, string> = {
    success: "border-mint-200 bg-mint-50 text-mint-700",
    failed: "border-rose-200 bg-rose-50 text-rose-700",
    partial: "border-amber-200 bg-amber-50 text-amber-700",
    "no-data": "border-slate-200 bg-slate-50 text-slate-500",
  };

  const badgeColors: Record<string, string> = {
    added: "bg-mint-100 text-mint-700",
    skipped: "bg-amber-100 text-amber-700",
    failed: "bg-rose-100 text-rose-700",
  };

  return (
    <div className={`rounded-2xl border p-5 sm:p-6 ${statusColors[overallStatus] || statusColors["no-data"]}`}>
      <div className="flex flex-col items-center gap-3 mb-4">
        <IconComponent className="h-8 w-8" />
        <span className="text-sm font-semibold">{summaryText}</span>
      </div>

      {/* Detailed results */}
      {results.length > 0 && (
        <div className="space-y-2 mb-4">
          {results.map((result, i) => (
            <div key={i} className="flex items-start gap-3 text-sm">
              <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ${badgeColors[result.status]}`}>
                {result.status === "added" ? <CheckCircle className="h-3 w-3" /> : result.status === "skipped" ? <Clock className="h-3 w-3" /> : <XCircle className="h-3 w-3" />}
                {result.status}
              </span>
              <div>
                <strong className="text-slate-900">{result.medicineName}</strong>
                <span className="ml-2 text-slate-500">
                  {result.status === "added" && "Added successfully"}
                  {result.status === "skipped" && "Skipped"}
                  {result.status === "failed" && `Failed: ${result.error || "Unknown error"}`}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Action buttons */}
      <div className="flex justify-center gap-3 mt-4">
        <button
          onClick={onViewInventory}
          className="h-11 rounded-2xl bg-brand-600 px-5 text-sm font-semibold text-white shadow-sm hover:bg-brand-700"
        >
          View Inventory
        </button>
        <button
          onClick={onScanAnother}
          className="h-11 rounded-2xl bg-white px-5 text-sm font-medium text-slate-700 ring-1 ring-slate-200 hover:bg-slate-50"
        >
          Scan Another
        </button>
      </div>
    </div>
  );
}