import { cn } from "@/lib/cn";
import { FileText } from "lucide-react";

const recordTypes = ["Prescription", "Medicine Bill", "Blood Report", "Doctor Notes"] as const;

type RecordType = (typeof recordTypes)[number];

const typeBadge: Record<RecordType, string> = {
  Prescription: "bg-brand-50 text-brand-700",
  "Medicine Bill": "bg-mint-50 text-mint-700",
  "Blood Report": "bg-rose-50 text-rose-700",
  "Doctor Notes": "bg-amber-50 text-amber-700",
};

interface RecordCardProps {
  title: string;
  hospital: string;
  date: string;
  recordType: RecordType;
  onClick?: () => void;
}

const previewGradients = [
  "from-brand-100 to-brand-50",
  "from-mint-100 to-mint-50",
  "from-violet-100 to-violet-50",
  "from-amber-100 to-amber-50",
];

export function RecordCard({ title, hospital, date, recordType, onClick }: RecordCardProps) {
  const gradient = previewGradients[title.length % previewGradients.length];

  return (
    <button
      type="button"
      onClick={onClick}
      className="group w-full rounded-3xl border border-slate-100 bg-white p-4 text-left shadow-soft transition hover:-translate-y-0.5 hover:shadow-md"
    >
      <div
        className={cn(
          "flex h-32 items-center justify-center rounded-2xl bg-gradient-to-br transition group-hover:scale-[1.02]",
          gradient,
        )}
      >
        <FileText className="h-10 w-10 text-slate-400" />
      </div>
      <div className="mt-3 space-y-1.5">
        <p className="truncate text-sm font-semibold text-slate-900">{title}</p>
        <p className="truncate text-xs text-slate-500">{hospital}</p>
        <p className="text-xs text-slate-400">{date}</p>
      </div>
      <span
        className={cn(
          "mt-2 inline-block rounded-full px-2.5 py-0.5 text-[11px] font-semibold",
          typeBadge[recordType],
        )}
      >
        {recordType}
      </span>
    </button>
  );
}