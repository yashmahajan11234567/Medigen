import { Folder } from "lucide-react";

interface FolderCardProps {
  name: string;
  count: number;
  onClick?: () => void;
}

const folderColors = [
  "bg-brand-50 text-brand-600",
  "bg-mint-50 text-mint-700",
  "bg-violet-50 text-violet-600",
  "bg-amber-50 text-amber-700",
  "bg-rose-50 text-rose-600",
  "bg-sky-50 text-sky-600",
  "bg-indigo-50 text-indigo-600",
];

export function FolderCard({ name, count, onClick }: FolderCardProps) {
  const colorIndex = name.length % folderColors.length;
  const color = folderColors[colorIndex];

  return (
    <button
      type="button"
      onClick={onClick}
      className="flex flex-col items-center gap-2 rounded-3xl border border-slate-100 bg-white p-5 shadow-soft transition hover:-translate-y-0.5 hover:shadow-md"
    >
      <div className={`flex h-14 w-14 items-center justify-center rounded-2xl ${color}`}>
        <Folder className="h-6 w-6" />
      </div>
      <p className="text-sm font-semibold text-slate-900">{name}</p>
      <p className="text-xs text-slate-400">{count} records</p>
    </button>
  );
}