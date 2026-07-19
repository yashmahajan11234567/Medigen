import { Download, Share2, Trash2 } from "lucide-react";

export function ActionButtons() {
  const buttons = [
    { icon: Download, label: "Download", accent: "bg-brand-50 text-brand-700 hover:bg-brand-100" },
    { icon: Share2, label: "Share", accent: "bg-mint-50 text-mint-700 hover:bg-mint-100" },
    { icon: Trash2, label: "Delete", accent: "bg-rose-50 text-rose-700 hover:bg-rose-100" },
  ];

  return (
    <div className="flex gap-3">
      {buttons.map((b) => (
        <button
          key={b.label}
          type="button"
          className={`flex flex-1 items-center justify-center gap-2 rounded-2xl py-3 text-sm font-semibold transition active:scale-[0.97] ${b.accent}`}
          aria-label={b.label}
        >
          <b.icon className="h-4 w-4" />
          {b.label}
        </button>
      ))}
    </div>
  );
}