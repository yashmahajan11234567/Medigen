import { Camera, FileImage, Package, Keyboard } from "lucide-react";
import { ScannerHeader } from "@/pages/scanner/components/ScannerHeader";
import { ScanOptionCard } from "@/pages/scanner/components/ScanOptionCard";
import { ImagePreview } from "@/pages/scanner/components/ImagePreview";
import { OCRPreviewCard } from "@/pages/scanner/components/OCRPreviewCard";
import { CompositionCard } from "@/pages/scanner/components/CompositionCard";
import { GenericResultCard } from "@/pages/scanner/components/GenericResultCard";
import { EmptyResults } from "@/pages/scanner/components/EmptyResults";

const scanOptions = [
  { title: "Take Photo", description: "Capture medicine strip with camera", icon: Camera, accent: "blue" as const },
  { title: "Upload Image", description: "Choose from your gallery", icon: FileImage, accent: "green" as const },
  { title: "Scan Box", description: "Scan medicine packaging barcode", icon: Package, accent: "amber" as const },
  { title: "Manual Entry", description: "Type medicine details", icon: Keyboard, accent: "purple" as const },
];

const dummyResults = [
  { name: "Pacimol 650 mg", composition: "Paracetamol 650 mg", strength: "650 mg", manufacturer: "Ipca Labs", available: true },
  { name: "Calpol 650 mg", composition: "Paracetamol 650 mg", strength: "650 mg", manufacturer: "GlaxoSmithKline", available: true },
  { name: "Dolo 650 mg", composition: "Paracetamol 650 mg", strength: "650 mg", manufacturer: "Micro Labs", available: true },
  { name: "Sumo 650 mg", composition: "Paracetamol 650 mg", strength: "650 mg", manufacturer: "Alkem Labs", available: false },
  { name: "Pyrigesic 650 mg", composition: "Paracetamol 650 mg", strength: "650 mg", manufacturer: "East India Pharma", available: true },
];

export function ScannerPage() {
  return (
    <div className="space-y-6">
      <ScannerHeader />

      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {scanOptions.map((opt) => (
          <ScanOptionCard key={opt.title} {...opt} />
        ))}
      </div>

      <ImagePreview />

      <div className="space-y-4">
        <OCRPreviewCard />

        <CompositionCard />
      </div>

      <button
        type="button"
        className="w-full rounded-2xl bg-brand-500 py-4 text-base font-semibold text-white shadow-lg shadow-brand-200 transition hover:bg-brand-600 active:scale-[0.98] sm:rounded-3xl sm:py-5 sm:text-lg"
      >
        Find Exact Generic
      </button>

      <div className="space-y-4">
        <div className="flex items-center gap-3">
          <div className="h-1 w-8 rounded-full bg-mint-500" />
          <h2 className="text-lg font-semibold text-slate-900">Generic Matches (5)</h2>
        </div>

        <div className="space-y-3">
          {dummyResults.map((r) => (
            <GenericResultCard key={r.name} {...r} />
          ))}
        </div>
      </div>

      <EmptyResults />
    </div>
  );
}