interface InfoRowProps {
  label: string;
  value: string;
}

function InfoRow({ label, value }: InfoRowProps) {
  return (
    <div className="flex items-center justify-between border-b border-slate-50 pb-3 last:border-none last:pb-0">
      <span className="text-sm text-slate-500">{label}</span>
      <span className="text-sm font-semibold text-slate-900">{value}</span>
    </div>
  );
}

const infoRows = [
  { label: "Full Name", value: "Arjun Mehta" },
  { label: "Age", value: "32" },
  { label: "Gender", value: "Male" },
  { label: "Blood Group", value: "B+" },
  { label: "Emergency Contact", value: "+91 99887 76655" },
  { label: "Primary Doctor", value: "Dr. Sharma" },
];

export function PersonalInfoCard() {
  return (
    <div className="rounded-3xl border border-slate-100 bg-white p-5 shadow-soft sm:p-6">
      <h3 className="mb-4 text-base font-semibold text-slate-900">Personal Information</h3>
      <div className="space-y-3">
        {infoRows.map((r) => (
          <InfoRow key={r.label} label={r.label} value={r.value} />
        ))}
      </div>
    </div>
  );
}