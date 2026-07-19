import { useEffect, useRef } from "react";
import { cn } from "@/lib/cn";
import { X } from "lucide-react";
import { PreviewPlaceholder } from "@/pages/medical-records/components/PreviewPlaceholder";
import { MetadataCard } from "@/pages/medical-records/components/MetadataCard";
import { ActionButtons } from "@/pages/medical-records/components/ActionButtons";

export interface RecordDetails {
  title: string;
  documentType: string;
  hospital: string;
  doctorName: string;
  visitDate: string;
  uploadDate: string;
  fileSize: string;
  category: string;
  notes: string;
}

interface RecordDrawerProps {
  open: boolean;
  record: RecordDetails | null;
  onClose: () => void;
}

export function RecordDrawer({ open, record, onClose }: RecordDrawerProps) {
  const drawerRef = useRef<HTMLDivElement>(null);

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

  useEffect(() => {
    if (!open) return;
    const timer = setTimeout(() => {
      drawerRef.current?.focus();
    }, 50);
    return () => clearTimeout(timer);
  }, [open]);

  if (!open || !record) return null;

  const previewType =
    record.documentType === "Prescription"
      ? ("prescription" as const)
      : record.documentType === "Medicine Bill"
        ? ("pdf" as const)
        : ("image" as const);

  return (
    <div className="fixed inset-0 z-50">
      <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" onClick={onClose} />

      <div
        ref={drawerRef}
        tabIndex={-1}
        className={cn(
          "fixed overflow-y-auto bg-white shadow-xl",
          "bottom-0 left-0 right-0 max-h-[85vh] rounded-t-3xl p-6",
          "sm:bottom-auto sm:left-auto sm:right-0 sm:top-0 sm:h-full sm:w-[420px] sm:max-h-none sm:rounded-none sm:rounded-l-3xl",
          "animate-[slideUp_250ms_ease-out] sm:animate-[slideInRight_250ms_ease-out]",
        )}
      >
        <div className="mb-5 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-slate-900">Record Details</h2>
          <button
            type="button"
            onClick={onClose}
            className="flex h-9 w-9 items-center justify-center rounded-xl text-slate-400 transition hover:bg-slate-100 hover:text-slate-600"
            aria-label="Close drawer"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="space-y-5">
          <PreviewPlaceholder type={previewType} />

          <div>
            <p className="text-lg font-semibold text-slate-900">{record.title}</p>
            <span className="mt-1 inline-block rounded-full bg-brand-50 px-3 py-0.5 text-xs font-semibold text-brand-700">
              {record.documentType}
            </span>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <MetadataCard label="Document Type" value={record.documentType} />
            <MetadataCard label="Hospital" value={record.hospital} />
            <MetadataCard label="Visit Date" value={record.visitDate} />
            <MetadataCard label="Upload Date" value={record.uploadDate} />
            <MetadataCard label="File Size" value={record.fileSize} />
            <MetadataCard label="Category" value={record.category} />
          </div>

          {record.doctorName && (
            <div>
              <p className="mb-1 text-xs font-medium text-slate-500">Doctor</p>
              <p className="text-sm font-semibold text-slate-900">{record.doctorName}</p>
            </div>
          )}

          {record.notes && (
            <div>
              <p className="mb-1 text-xs font-medium text-slate-500">Notes</p>
              <p className="rounded-2xl bg-slate-50 p-3 text-sm leading-6 text-slate-700">{record.notes}</p>
            </div>
          )}

          <ActionButtons />
        </div>
      </div>
    </div>
  );
}