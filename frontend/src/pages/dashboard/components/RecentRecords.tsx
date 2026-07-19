import { FileText } from "lucide-react";
import { Card } from "@/components/common/Card";
import { SectionTitle } from "@/pages/dashboard/components/SectionTitle";

interface RecordItem {
  title: string;
  hospital: string;
  date: string;
}

export function RecentRecords({ recentRecords }: { recentRecords: RecordItem[] }) {
  if (recentRecords.length === 0) return null;

  return (
    <Card className="p-5 sm:p-6">
      <SectionTitle>Recent Medical Records</SectionTitle>

      <div className="mt-5 space-y-3">
        {recentRecords.map((record) => (
          <div
            key={record.title}
            className="flex items-center gap-4 rounded-2xl border border-slate-100 bg-white p-4 transition hover:shadow-sm"
          >
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-violet-50 text-violet-600">
              <FileText className="h-5 w-5" />
            </div>
            <div className="min-w-0 flex-1">
              <p className="font-semibold text-slate-900">{record.title}</p>
              <p className="mt-0.5 text-sm text-slate-500">{record.hospital}</p>
            </div>
            <span className="shrink-0 text-xs text-slate-400">{record.date}</span>
          </div>
        ))}
      </div>
    </Card>
  );
}