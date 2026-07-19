import { useEffect, useRef } from "react";
import { cn } from "@/lib/cn";
import { X, FileImage } from "lucide-react";
import { UploadOptionCard } from "@/pages/medical-records/components/UploadOptionCard";

interface UploadModalProps {
  open: boolean;
  onClose: () => void;
}

export function UploadModal({ open, onClose }: UploadModalProps) {
  const overlayRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    document.addEventListener("keydown", handleKey);
    return () => document.removeEventListener("keydown", handleKey);
  }, [open, onClose]);

  useEffect(() => {
    if (open) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
    return () => {
      document.body.style.overflow = "";
    };
  }, [open]);

  if (!open) return null;

  return (
    <div
      ref={overlayRef}
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm"
      onClick={(e) => {
        if (e.target === overlayRef.current) onClose();
      }}
    >
      <div
        className={cn(
          "mx-4 w-full max-w-md rounded-3xl border border-slate-100 bg-white p-6 shadow-xl",
          "animate-[fadeIn_200ms_ease-out]",
        )}
      >
        <div className="mb-5 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-brand-100 text-brand-600">
              <FileImage className="h-5 w-5" />
            </div>
            <h2 className="text-lg font-semibold text-slate-900">Upload Record</h2>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="flex h-9 w-9 items-center justify-center rounded-xl text-slate-400 transition hover:bg-slate-100 hover:text-slate-600"
            aria-label="Close modal"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="space-y-3">
          <UploadOptionCard icon="camera" label="Take Photo" selected={false} onClick={() => {}} />
          <UploadOptionCard icon="image" label="Upload Image" selected={false} onClick={() => {}} />
          <UploadOptionCard icon="pdf" label="Upload PDF" selected={false} onClick={() => {}} />
        </div>

        <div className="mt-5 rounded-2xl bg-slate-50 p-4">
          <p className="text-xs font-semibold text-slate-600">Supported Formats</p>
          <div className="mt-2 flex flex-wrap gap-2">
            <span className="rounded-full bg-white px-3 py-1 text-xs font-medium text-slate-700 shadow-sm">JPG</span>
            <span className="rounded-full bg-white px-3 py-1 text-xs font-medium text-slate-700 shadow-sm">PNG</span>
            <span className="rounded-full bg-white px-3 py-1 text-xs font-medium text-slate-700 shadow-sm">PDF</span>
          </div>
          <p className="mt-2 text-xs text-slate-500">
            Maximum Size: <span className="font-semibold text-slate-700">10 MB</span>
          </p>
        </div>
      </div>
    </div>
  );
}