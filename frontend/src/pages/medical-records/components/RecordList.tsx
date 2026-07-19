import { cn } from "@/lib/cn";

const recordTypes = ["Prescription", "Medicine Bill", "Blood Report", "Doctor Notes"] as const;

type RecordType = (typeof recordTypes)[number];

const typeBadge: Record<RecordType, string> = {
  Prescription: "bg-brand-50 text-brand-700",
  "Medicine Bill": "bg-mint-50 text-mint-700",
  "Blood Report": "bg-rose-50 text-rose-700",
  "Doctor Notes": "bg-amber-50 text-amber-700",
};

interface RecordListRow {
  title: string;
  hospital: string;
  date: string;
  recordType: RecordType;
}

interface RecordListProps {
  records: RecordListRow[];
  onRecordClick?: (index: number) => void;
}

export function RecordList({ records, onRecordClick }: RecordListProps) {
  return (
    <div className="overflow-hidden rounded-3xl border border-slate-100 bg-white shadow-soft">
      <table className="w-full text-left text-sm">
        <thead>
          <tr className="border-b border-slate-100 bg-slate-50">
            <th className="px-5 py-3.5 text-xs font-semibold uppercase tracking-wider text-slate-500">
              Title
            </th>
            <th className="px-5 py-3.5 text-xs font-semibold uppercase tracking-wider text-slate-500">
              Hospital
            </th>
            <th className="hidden px-5 py-3.5 text-xs font-semibold uppercase tracking-wider text-slate-500 sm:table-cell">
              Date
            </th>
            <th className="px-5 py-3.5 text-xs font-semibold uppercase tracking-wider text-slate-500">
              Record Type
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-50">
          {records.map((r, i) => (
            <tr
              key={r.title}
              onClick={() => onRecordClick?.(i)}
              className="cursor-pointer transition hover:bg-slate-50/50"
            >
              <td className="px-5 py-4 font-medium text-slate-900">{r.title}</td>
              <td className="px-5 py-4 text-slate-600">{r.hospital}</td>
              <td className="hidden px-5 py-4 text-slate-500 sm:table-cell">{r.date}</td>
              <td className="px-5 py-4">
                <span
                  className={cn(
                    "inline-block rounded-full px-2.5 py-0.5 text-[11px] font-semibold",
                    typeBadge[r.recordType],
                  )}
                >
                  {r.recordType}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}