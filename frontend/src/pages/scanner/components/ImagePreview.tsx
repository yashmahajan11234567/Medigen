import { useState, useEffect, useRef } from "react";
import { Button } from "../components/common/Button";
import { Input as InputComponent } from "../components/common/Input";
import { cn } from "@/lib/cn";
import { LoadingScreen } from "@/components/common/LoadingScreen";
import { PageError } from "@/components/feedback/PageError";
import { ocrService } from "@/services/ocr.service";
import type { OcrExtractedMedicine } from "@/services/ocr.service";
import { useToast } from "@/components/ui/ToastProvider";

export function ImagePreview() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string>("");
  const [uploading, setUploading] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [ocrResults, setOcrResults] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);
  const processingRef = useRef<number>(0); // track active processes
  const { addToast } = useToast();

  // Generate preview URL when file changes
  useEffect(() => {
    if (selectedFile) {
      const url = URL.createObjectURL(selectedFile);
      setPreviewUrl(url);
      return () => URL.revokeObjectURL(url);
    } else {
      setPreviewUrl("");
    }
  }, [selectedFile]);

  // Handle file selection
  const onFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  // Upload and process image
  const startOcr = async () => {
    if (!selectedFile) return;

    const processId = ++processingRef.current;
    setError(null);
    setOcrResults([]);
    setUploading(true);

    try {
      const formData = new FormData();
      formData.append("file", selectedFile);

      // Call OCR service
      const result = await ocrService.processImage(formData);
      setOcrResults(result as OcrExtractedMedicine[]);

      // Show success toast
      addToast({
        title: "OCR completed",
        description: `${result.length} medicines extracted successfully.`,
        variant: "success",
      });
    } catch (err: any) {
      console.error("OCR processing failed:", err);
      setError(err.message || "OCR processing failed");
      setOcrResults([]);
      addToast({
        title: "OCR failed",
        description: err.message || "Failed to process image",
        variant: "error",
      });
    } finally {
      setProcessing(false);
      // If a newer process started, discard results of this one
      if (processingRef.current > processId) {
        setOcrResults([]);
      }
      setUploading(false);
    }
  };

  // Render progress indicator
  const renderProgress = () => {
    if (uploading) {
      return <loadingScreen title="Uploading..." description="Please wait while the file uploads..." />;
    }
    if (processing) {
      return <loadingScreen title="Processing OCR..." description="Analyzing the image and extracting medicine details..." />;
    }
    return null;
  };

  return (
    <div className="flex flex-col items-center justify-center rounded-3xl border-2 border-dashed border-slate-200 bg-white/50 p-12 text-center relative">
      {/* Preview icon */}
      <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-slate-100 text-slate-400">
        {selectedFile ? (
          // Show a simple image preview
          <img
            src={previewUrl}
            alt="preview"
            className="h-7 w-7 object-cover rounded-2xl"
          />
        ) : (
          <svg
            className="h-7 w-7 text-slate-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M7 16v8a4 4 0 008 0v-8a4 4 0 00-8 0zM3 7a1 1 0 011 0v1A1 1 0 012 9h6a1 1 0 010 2H5v-1a1 1 0 011-1zM3 13a1 1 0 011 0v1A1 1 0 012 15h6a1 1 0 010-2H5z"
            />
          </svg>
        )}
      </div>

      <p className="mt-4 text-sm text-slate-500">
        {selectedFile ? selectedFile.name : "No image selected"}
      </p>

      {/* Hidden file input */}
      <InputComponent
        type="file"
        accept="image/*"
        onChange={onFileChange}
        className="hidden"
      />

      {/* Browse button */}
      <Button
        type="button"
        variant="secondary"
        className="mt-2 rounded-md bg-slate-200 text-slate-800 px-4 py-2 hover:bg-slate-300"
        onClick={() => {
          // Trigger the hidden file input
          const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
          fileInput?.click();
        }}
      >
        Browse Image
      </Button>

      {/* Upload / Process button */}
      {selectedFile && !processing && (
        <Button
          type="button"
          variant="primary"
          disabled={uploading}
          className="mt-2 rounded-md px-4 py-2 text-white hover:bg-brand-600"
        >
          {uploading ? "Uploading..." : "Start OCR"}
        </Button>
      )}

      {/* Loading indicators */}
      {renderProgress()}

      {/* Error display */}
      {error && (
        <PageError
          title="OCR Error"
          description={error}
          onRetry={startOcr}
        />
      )}

      {/* OCR Results display */}
      {ocrResults.length > 0 && (
        <div className="mt-4 space-y-3">
          <h3 className="text-sm font-semibold text-slate-900">Extracted Medicines</h3>
          {ocrResults.map((med) => (
            <div
              key={med.id}
              className="rounded border border-slate-100 bg-white p-3 text-sm text-slate-900"
            >
              <p className="font-medium">{med.name}</p>
              {med.generic_name && (
                <p className="text-xs text-slate-600">Generic: {med.generic_name}</p>
              )}
              <p className="text-xs text-slate-500">
                Strength: {med.composition?.strength ?? "N/A"}
              </p>
              <p className="text-xs text-slate-500">
                Ingredient: {med.composition?.ingredient ?? "N/A"}
              </p>
              {med.confidence && (
                <p className="text-xs text-gray-500">Confidence: {med.confidence.toFixed(1)}%</p>
              )}
              <div className="mt-2 flex gap-2">
                {/* Forward to Generic Finder */}
                <Button
                  type="button"
                  variant="ghost"
                  className="rounded-md px-3 py-1.5 text-xs text-slate-800 hover:bg-slate-200"
                  onClick={() => {
                    // In a real implementation, this would push the medicine name
                    // to the Generic Finder search field or store.
                    console.log("Forward to Generic Finder:", med.name);
                  }}
                >
                  Send to Generic Finder
                </Button>

                {/* Add to Inventory (sample implementation) */}
                <Button
                  type="button"
                  variant="ghost"
                  className="rounded-md px-3 py-1.5 text-xs text-slate-800 hover:bg-slate-200"
                  onClick={async () => {
                    try {
                      await fetch("/api/v1/generic/add-to-inventory", {
                        method: "POST",
                        headers: {
                          "Content-Type": "application/json",
                        },
                        body: JSON.stringify({
                          medicine_id: med.id,
                          quantity: null,
                          quantity_unit: null,
                          expiry_date: null,
                        }),
                      });
                      addToast({
                        title: "Added to inventory",
                        description: `${med.name} added successfully`,
                        variant: "success",
                      });
                    } catch {
                      addToast({
                        title: "Add failed",
                        description: "Could not add to inventory",
                        variant: "error",
                      });
                    }
                  }}
                >
                  Add to Inventory
                </Button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}