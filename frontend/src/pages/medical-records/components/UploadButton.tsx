import { cn } from "@/lib/cn";
import { Upload } from "lucide-react";

interface UploadButtonProps {
  onClick: () => void;
}

export function UploadButton({ onClick }: UploadButtonProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        "fixed bottom-6 z-40 flex items-center gap-2 rounded-2xl bg-brand-500 px-5 py-3.5 text-sm font-semibold text-white shadow-lg shadow-brand-200 transition hover:bg-brand-600 active:scale-[0.97]",
        "left-1/2 -translate-x-1/2",
        "sm:left-auto sm:right-6 sm:translate-x-0",
      )}
      aria-label="Upload Record"
    >
      <Upload className="h-4 w-4" />
      Upload Record
    </button>
  );
}