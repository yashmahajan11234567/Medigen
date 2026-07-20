import { useRef, useEffect } from "react";
import { Upload, Image as ImageIcon, AlertCircle } from "lucide-react";

interface ImagePreviewProps {
  selectedFile: File | null;
  previewUrl: string;
  status: "idle" | "uploading" | "processing" | "success" | "error";
  scanMode: "composition" | "pharmacy-bill" | "document";
  error: string | null;
  onFileSelect: (file: File) => void;
  onStartScan: () => void;
  onClear: () => void;
}

const MODE_LABELS: Record<string, string> = {
  composition: "Scan Composition",
  "pharmacy-bill": "Scan Bill",
  document: "Scan Document",
};

export function ImagePreview({
  selectedFile,
  previewUrl,
  status,
  scanMode,
  error,
  onFileSelect,
  onStartScan,
  onClear,
}: ImagePreviewProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const isBusy = status === "uploading" || status === "processing";

  // Revoke object URL on unmount / change
  useEffect(() => {
    return () => {
      if (previewUrl) URL.revokeObjectURL(previewUrl);
    };
  }, [previewUrl]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) onFileSelect(file);
  };

  return (
    <div className="flex flex-col items-center justify-center rounded-3xl border-2 border-dashed border-slate-200 bg-white/50 p-12 text-center relative">
      {/* Preview */}
      <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-slate-100 text-slate-400">
        {selectedFile && previewUrl ? (
          <img
            src={previewUrl}
            alt="preview"
            className="h-full w-full rounded-2xl object-cover"
          />
        ) : (
          <ImageIcon className="h-7 w-7" />
        )}
      </div>

      <p className="mt-4 text-sm text-slate-500">
        {selectedFile ? selectedFile.name : "No image selected"}
      </p>

      {/* Hidden file input */}
      <input
        ref={inputRef}
        type="file"
        accept="image/png,image/jpeg,image/jpg"
        onChange={handleChange}
        className="hidden"
      />

      {/* Browse button */}
      <button
        type="button"
        disabled={isBusy}
        onClick={() => inputRef.current?.click()}
        className="mt-2 inline-flex items-center gap-2 rounded-md bg-slate-200 px-4 py-2 text-sm text-slate-800 transition hover:bg-slate-300 disabled:opacity-50"
      >
        <Upload className="h-4 w-4" />
        Browse Image
      </button>

      {/* Start Scan button */}
      {selectedFile && !isBusy && status !== "success" && (
        <button
          type="button"
          onClick={onStartScan}
          className="mt-3 rounded-md bg-brand-500 px-6 py-2 text-sm font-medium text-white transition hover:bg-brand-600 active:scale-[0.98]"
        >
          {MODE_LABELS[scanMode]}
        </button>
      )}

      {/* Done — clear & scan again */}
      {selectedFile && status === "success" && (
        <button
          type="button"
          onClick={onClear}
          className="mt-3 rounded-md bg-slate-200 px-6 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-300"
        >
          Scan Another
        </button>
      )}

      {/* Processing spinner */}
      {isBusy && (
        <div className="mt-4 flex items-center gap-2 text-sm text-brand-600">
          <div className="h-4 w-4 animate-spin rounded-full border-2 border-brand-200 border-t-brand-600" />
          <span>
            {status === "uploading" ? "Uploading..." : "Processing OCR..."}
          </span>
        </div>
      )}

      {/* Error display */}
      {error && status === "error" && (
        <div className="mt-4 flex items-start gap-2 rounded-xl bg-rose-50 p-3 text-left text-sm text-rose-700">
          <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}
    </div>
  );
}