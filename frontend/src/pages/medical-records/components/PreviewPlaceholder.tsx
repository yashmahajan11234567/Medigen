import { FileText, Image, File } from "lucide-react";
import { cn } from "@/lib/cn";

interface PreviewPlaceholderProps {
  type: "prescription" | "image" | "pdf";
  className?: string;
}

const icons = {
  prescription: FileText,
  image: Image,
  pdf: File,
};

const gradients = {
  prescription: "from-brand-100 to-brand-50",
  image: "from-violet-100 to-violet-50",
  pdf: "from-rose-100 to-rose-50",
};

export function PreviewPlaceholder({ type, className }: PreviewPlaceholderProps) {
  const Icon = icons[type];
  const gradient = gradients[type];

  return (
    <div
      className={cn(
        "flex h-48 items-center justify-center rounded-3xl bg-gradient-to-br sm:h-56",
        gradient,
        className
      )}
    >
      <div className="flex flex-col items-center gap-2">
        <Icon className="h-10 w-10 text-slate-400" />
        <span className="text-xs font-medium uppercase tracking-wider text-slate-400">
          {type === "prescription" ? "Prescription" : type === "image" ? "Image" : "PDF"} Preview
        </span>
      </div>
    </div>
  );
}