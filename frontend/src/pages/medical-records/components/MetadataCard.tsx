interface MetadataCardProps {
  label: string;
  value: string;
}

export function MetadataCard({ label, value }: MetadataCardProps) {
  return (
    <div className="rounded-2xl bg-slate-50 px-4 py-3">
      <p className="text-xs font-medium text-slate-500">{label}</p>
      <p className="mt-0.5 text-sm font-semibold text-slate-900">{value}</p>
    </div>
  );
}