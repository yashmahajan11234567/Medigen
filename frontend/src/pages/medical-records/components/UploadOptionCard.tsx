import { cn } from "@/lib/cn";

interface UploadOptionCardProps {
  icon: "camera" | "image" | "pdf";
  label: string;
  selected: boolean;
  onClick: () => void;
}

const emojiIcon = {
  camera: "📷",
  image: "🖼",
  pdf: "📄",
};

export function UploadOptionCard({ icon, label, selected, onClick }: UploadOptionCardProps) {
  const emoji = emojiIcon[icon];

  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        "flex w-full items-center gap-4 rounded-2xl border-2 p-4 text-left transition",
        selected
          ? "border-brand-200 bg-brand-50"
          : "border-slate-100 bg-white hover:border-slate-200 hover:bg-slate-50",
      )}
    >
      <div
        className={cn(
          "flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl text-lg",
          selected ? "bg-brand-100" : "bg-slate-100",
        )}
      >
        <span className="sr-only">{label}</span>
        <span>{emoji}</span>
      </div>
      <div>
        <p className="text-sm font-semibold text-slate-900">{label}</p>
        <p className="text-xs text-slate-500">
          {icon === "camera" ? "Capture using camera" : icon === "image" ? "Choose from gallery" : "Select a PDF file"}
        </p>
      </div>
    </button>
  );
}