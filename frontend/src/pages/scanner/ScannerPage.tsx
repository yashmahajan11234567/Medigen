import { useState, useCallback, useRef, useEffect } from "react";
import { Camera, FileImage, Package, Keyboard } from "lucide-react";
import { ScannerHeader } from "@/pages/scanner/components/ScannerHeader";
import { ScanOptionCard } from "@/pages/scanner/components/ScanOptionCard";
import { ImagePreview } from "@/pages/scanner/components/ImagePreview";
import { OCRPreviewCard } from "@/pages/scanner/components/OCRPreviewCard";
import { CompositionCard } from "@/pages/scanner/components/CompositionCard";
import { GenericResultCard } from "@/pages/scanner/components/GenericResultCard";
import { EmptyResults } from "@/pages/scanner/components/EmptyResults";
import { ocrService } from "@/services/ocr.service";
import { useToast } from "@/components/ui/ToastProvider";
import type {
  OCRCompositionResponse,
  OCRPharmacyBillResponse,
  OCRDocumentResponse,
  GenericMedicineSummary,
} from "@/types/api";

import InventoryPanel from "./components/InventoryPanel";
import SubmissionSummary from "./components/SubmissionSummary";

import MedicineChecklistItem from "./components/MedicineChecklistItem";
import type { MedicineForInventory, SubmissionResultItem } from "@/types/api";

import { genericFinderService } from "@/services/genericFinder.service";

import MedicalRecordPreview from "./components/MedicalRecordPreview";

import { medicalRecordsService } from "@/services/medicalRecords.service";
import type {
  MedicalRecordCreateRequest,
  MedicalRecordDocumentCreate,
} from "@/types/api";

type InventoryPhase = 'hidden' | 'preview' | 'submitting' | 'complete';
type ScanMode = "composition" | "pharmacy-bill" | "document";
type PageStatus = "idle" | "uploading" | "processing" | "success" | "error";

type OcrData =
  | { mode: "composition"; data: OCRCompositionResponse }
  | { mode: "pharmacy-bill"; data: OCRPharmacyBillResponse }
  | { mode: "document"; data: OCRDocumentResponse };
export function ScannerPage() {
  const { addToast } = useToast();
  const fileInputRef = useRef<HTMLInputElement>(null);

  // NEW STATE FOR INVENTORY WORKFLOW
  const [scanMode, setScanMode] = useState<ScanMode>("composition");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string>("");
  const [status, setStatus] = useState<PageStatus>("idle");
  const [error, setError] = useState<string | null>(null);
  const [ocrData, setOcrData] = useState<OcrData | null>(null);

  // NEW: Inventory workflow state
  const [inventoryPhase, setInventoryPhase] = useState<InventoryPhase>("hidden");
  const [inventoryItems, setInventoryItems] = useState<MedicineForInventory[]>([]);
  const [submissionResults, setSubmissionResults] = useState<SubmissionResultItem[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [selectedCount, setSelectedCount] = useState(0);
  const [isLookingUp, setIsLookingUp] = useState<Record<string, boolean>>({});

  // NEW: Medical record workflow state
  const [medicalRecordPhase, setMedicalRecordPhase] = useState<'hidden' | 'preview' | 'saving' | 'complete'>('hidden');
  const [medicalRecordDraft, setMedicalRecordDraft] = useState<MedicalRecordCreateRequest | null>(null);
  const [isSavingMedicalRecord, setIsSavingMedicalRecord] = useState(false);
  const [medicalRecordSaveError, setMedicalRecordSaveError] = useState<string | null>(null);

  // Scan options
  const scanOptions = [
    {
      key: "composition",
      label: "Composition",
      icon: <Package className="h-5 w-5" />,
      description: "Scan medicine compositions",
    },
    {
      key: "pharmacy-bill",
      label: "Pharmacy Bill",
      icon: <FileImage className="h-5 w-5" />,
      description: "Scan pharmacy bills",
    },
    {
      key: "document",
      label: "Medical Document",
      icon: <Keyboard className="h-5 w-5" />,
      description: "Scan medical documents",
    },
  ];

  const handleResolveDuplicate = useCallback((action: string, item: MedicineForInventory) => {
    // Implement duplicate resolution logic if needed
    console.log("Resolve duplicate:", action, item);
  }, []);

  const handleFileSelect = useCallback((file: File) => {
    setSelectedFile(file);
    setStatus("idle");
    setError(null);
    setOcrData(null);
    setInventoryPhase("hidden");
    setInventoryItems([]);
    setSubmissionResults([]);
  }, []);

  const handleClear = useCallback(() => {
    setSelectedFile(null);
    setPreviewUrl("");
    setStatus("idle");
    setError(null);
    setOcrData(null);
    setInventoryPhase("hidden");
    setInventoryItems([]);
    setSubmissionResults([]);
    setMedicalRecordDraft(null);
    setMedicalRecordPhase("hidden");
    setIsSavingMedicalRecord(false);
    setMedicalRecordSaveError(null);
  }, []);

  // NEW: Build inventory items from OCR data
  const buildInventoryItems = useCallback((ocrData: OcrData): MedicineForInventory[] => {
    const items: MedicineForInventory[] = [];

    if (!ocrData) return items;

    switch (ocrData.mode) {
      case "composition": {
        // Generic matches are typically "known" medicines
        (ocrData.data.result.matches || []).forEach(match => {
          items.push({
            id: match.id.toString(),
            medicineId: match.id,
            name: match.name,
            genericName: match.generic_name,
            brandName: match.brand_name,
            type: match.composition.dosage_form as any, // Convert to frontend enum
            strength: match.composition.strength,
            dosageUnit: match.composition.unit,
            quantity: null,
            quantityUnit: null,
            expiryDate: null,
            isSelected: true, // All selected by default
            isKnown: true,
            isDuplicate: false,
            existingInventoryItem: null,
            submissionStatus: "pending",
            error: null,
          });
        });
        break;
      }
      case "pharmacy-bill": {
        (ocrData.data.result.medicines || []).forEach((medicine) => {
          items.push({
            id: `bill-${medicine.medicine_id || Date.now()}`,
            medicineId: medicine.medicine_id || null,
            name: medicine.medicine_name,
            genericName: medicine.generic_name,
            brandName: medicine.brand_name,
            type: "other", // Default type for unknown
            strength: medicine.strength,
            dosageUnit: medicine.dosage_unit,
            quantity: medicine.quantity || 1,
            quantityUnit: null,
            expiryDate: null,
            isSelected: true,
            isKnown: false,
            isDuplicate: false,
            existingInventoryItem: null,
            error: null,
          });
        });
        break;
      }
      case "document": {
        // For document scans, we use the extracted medicines
        // This would typically come from parsing the document
        // For now, we'll use the document info but not create inventory items
        // In a full implementation, we'd extract medicines from the document
        break;
      }
    }

    return items;
  }, []);

  // NEW: Handle toggle selection
  const handleToggle = useCallback((id: string) => {
    // Update selected state in inventoryItems
    setInventoryItems((prev) =>
      prev.map((item) =>
        item.id === id ? { ...item, isSelected: !item.isSelected } : item
      )
    );

    // Update selectedCount
    const selected = inventoryItems.filter((i) => i.isSelected);
    setSelectedCount(selected.length);
  }, [inventoryItems]);

  // NEW: Handle select all
  const handleSelectAll = useCallback(() => {
    setInventoryItems((prev) =>
      prev.map((item) => ({ ...item, isSelected: true }))
    );
    setSelectedCount(inventoryItems.length);
  }, [inventoryItems]);

  // NEW: Handle clear all
  const handleClearAll = useCallback(() => {
    setInventoryItems((prev) =>
      prev.map((item) => ({ ...item, isSelected: false }))
    );
    setSelectedCount(0);
  }, [inventoryItems]);

  // NEW: Handle edit (name, type, etc.)
  const handleEdit = useCallback((id: string, field: string, value: string) => {
    setInventoryItems((prev) =>
      prev.map((item) =>
        item.id === id ? { ...item, [field]: value } : item
      )
    );
  }, []);

  // NEW: Handle lookup for unknown medicines
  const handleLookup = useCallback((id: string) => {
    const item = inventoryItems.find((i) => i.id === id);
    if (!item || item.isKnown) return;

    setIsLookingUp((prev) => ({ ...prev, [id]: true }));

    // Call generic finder search
    const name = item.name;
    genericFinderService.search(name)
      .then((result) => {
        // Simple matching: find first result and treat as match
        const matchedMedicine = result.result.source_medicine;
        if (matchedMedicine) {
          setInventoryItems((prev) =>
            prev.map((i) =>
              i.id === id
                ? {
                    ...i,
                    isKnown: true,
                    medicineId: matchedMedicine.id,
                    genericName: matchedMedicine.generic_name,
                    brandName: matchedMedicine.brand_name,
                    type: matchedMedicine.composition.dosage_form as any,
                    strength: matchedMedicine.composition.strength,
                    dosageUnit: matchedMedicine.composition.unit,
                  }
                : i
            )
          );
          setIsLookingUp((prev) => ({ ...prev, [id]: false }));
        }
      })
      .catch((err) => {
        setInventoryItems((prev) =>
          prev.map((i) =>
            i.id === id ? { ...i, error: err.message } : i
          )
        );
        setIsLookingUp((prev) => ({ ...prev, [id]: false }));
      });
  }, [inventoryItems]);

  const handleSubmitToInventory = useCallback(async (item: MedicineForInventory) => {
    if (isSubmitting) return;
    setIsSubmitting(true);
    try {
      const response = await apiClient.post('/inventory', {
        medicine_id: item.medicineId,
        name: item.name,
        generic_name: item.genericName,
        brand_name: item.brandName,
        type: item.type,
        quantity: item.quantity,
        quantity_unit: item.quantityUnit,
        expiry_date: item.expiryDate,
      });
      // Update item with success
      setInventoryItems((prev) =>
        prev.map((i) =>
          i.id === item.id
            ? { ...i, status: 'added', error: null, inventoryItemId: response.data.id }
            : i
        )
      );
      addToast({ title: 'Item added to inventory', variant: 'success' });
    } catch (err: any) {
      setInventoryItems((prev) =>
        prev.map((i) =>
          i.id === item.id ? { ...i, status: 'failed', error: err.message || 'Submission failed' } : i
        )
      );
      addToast({ title: 'Error adding item', variant: 'error' });
    } finally {
      setIsSubmitting(false);
    }
  }, [isSubmitting, addToast, apiClient]);

  const handleSubmitAll = useCallback(async () => {
    if (isSubmitting) return;
    setIsSubmitting(true);

    const results: SubmissionResultItem[] = [];

    for (const item of inventoryItems.filter((i) => i.isSelected)) {
      try {
        if (item.isDuplicate && item.existingInventoryItem) {
          // Handle duplicate: update quantity or skip or separate
          // Simplified: always add for now
          results.push({ ...item, status: "added", error: null });
        } else {
          // Submit new item
          const response = await apiClient.post("/inventory", {
            medicine_id: item.medicineId,
            name: item.name,
            generic_name: item.genericName,
            brand_name: item.brandName,
            type: item.type,
            quantity: item.quantity,
            quantity_unit: item.quantityUnit,
            expiry_date: item.expiryDate,
          });

          results.push({
            ...item,
            status: "added",
            error: null,
            inventoryItemId: response.data.id,
          });
        }
      } catch (err: any) {
        results.push({
          ...item,
          status: "failed",
          error: err.message || "Submission failed",
        });
      }
    }

    // Update state
    setSubmissionResults(results);
    setInventoryPhase("complete");

    // Show toast with summary
    const added = results.filter((r) => r.status === "added").length;
    const skipped = results.filter((r) => r.status === "skipped").length;
    const failed = results.filter((r) => r.status === "failed").length;

    addToast({
      title: `${added} added, ${skipped} skipped, ${failed} failed`,
      variant: "success",
    });

    setIsSubmitting(false);
  }, [inventoryItems, addToast, apiClient]);

  // EXISTING HANDLERS
  const handleScanOption = useCallback(
    (key: string) => {
      setScanMode(key as ScanMode);
      setSelectedFile(null);
      setPreviewUrl("");
      setStatus("idle");
      setError(null);
      setOcrData(null);
      setInventoryPhase("hidden");
      setInventoryItems([]);
      setSubmissionResults([]);
      setIsSubmitting(false);
      setSelectedCount(0);
      setIsLookingUp({});
      setMedicalRecordDraft(null);
      setMedicalRecordPhase("hidden");
      setIsSavingMedicalRecord(false);
      setMedicalRecordSaveError(null);
    },
    []
  );

  const handleStartScan = useCallback(async () => {
    if (!selectedFile) return;
    setStatus("uploading");
    try {
      // For document scans, we call the OCR document endpoint
      if (scanMode === "document") {
        setStatus("processing");
        const response = await ocrService.document(selectedFile);
        // Build medical record draft from OCR response
        const draft: MedicalRecordCreateRequest = {
          title: `${response.data.patient_name ?? 'Unknown Patient'} – ${response.data.document_type}`,
          folder_name: "Inbox", // default folder
          hospital_name: response.data.hospital_or_lab ?? null,
          doctor_name: response.data.doctor_name ?? null,
          visit_date: response.data.report_date ?? null,
          diagnosis: response.data.diagnosis_text ?? null,
          notes: response.data.notes ?? null,
          treatment_name: null, // not extracted by OCR
          description: null,
          documents: [
            {
              document_type: response.data.document_type as MedicalRecordDocumentType,
              file_name: response.data.file_name ?? selectedFile.name,
              file_type: response.data.file_type ?? selectedFile.type,
              file_size: response.data.file_size ?? selectedFile.size,
              storage_path: response.data.storage_path ?? "",
              upload_date: new Date().toISOString(),
              doctor_name: response.data.doctor_name ?? null,
              hospital_or_clinic: response.data.hospital_or_lab ?? null,
              // OCR metadata
              ocr_confidence: response.data.ocr_confidence ?? null,
              ocr_processed_at: new Date().toISOString(),
              ocr_source: "upload", // we don't have camera yet, so assumes upload; could be extended for camera
              blur_score: response.data.blur_score ?? null,
              brightness: response.data.brightness ?? null,
              contrast: response.data.contrast ?? null,
              is_pass: response.data.is_pass ?? null,
              issues: response.data.issues ?? [],
            },
          ],
          linked_schedule_ids: [],
          linked_inventory_item_ids: [],
          linked_medicine_ids: [],
          linked_generic_search_ids: [],
        };
        setMedicalRecordDraft(draft);
        setMedicalRecordPhase("preview");
        setStatus("success");
      } else {
        // For composition and pharmacy-bill, we keep the existing inventory flow
        setStatus("processing");
        // Process OCR based on scan mode
        let ocrResponse: OCRCompositionResponse | OCRPharmacyBillResponse;
        if (scanMode === "composition") {
          ocrResponse = await ocrService.composition(selectedFile);
        } else if (scanMode === "pharmacy-bill") {
          ocrResponse = await ocrService.pharmacyBill(selectedFile);
        } else {
          throw new Error("Invalid scan mode");
        }
        // Set OCR data
        if (scanMode === "composition") {
          setOcrData({ mode: "composition", data: ocrResponse });
        } else if (scanMode === "pharmacy-bill") {
          setOcrData({ mode: "pharmacy-bill", data: ocrResponse });
        }
        // Build inventory items from OCR data
        const inventoryItems = buildInventoryItems(ocrData as OcrData);
        setInventoryItems(inventoryItems);
        setInventoryPhase("preview");
        setStatus("success");
      }
    } catch (err: any) {
      setError(
        err.response?.data?.message ||
          err.message ||
          "Failed to process document"
      );
      setStatus("error");
    }
  }, [selectedFile, scanMode, addToast, ocrService, buildInventoryItems]);

  // NEW: Save medical record
  const handleSaveMedicalRecord = useCallback(async () => {
    if (!medicalRecordDraft) return;
    setIsSavingMedicalRecord(true);
    setMedicalRecordSaveError(null);
    try {
      await medicalRecordsService.create(medicalRecordDraft);
      addToast({ title: "Medical record saved", variant: "success" });
      // Clear draft and redirect
      setMedicalRecordDraft(null);
      setMedicalRecordPhase("hidden");
      // Redirect to medical records page
      window.location.href = "/medical-records";
    } catch (err: any) {
      setMedicalRecordSaveError(
        err.response?.data?.message ||
          err.message ||
          "Failed to save medical record"
      );
      addToast({ title: "Error saving record", variant: "error" });
    } finally {
      setIsSavingMedicalRecord(false);
    }
  }, [medicalRecordDraft, medicalRecordsService, addToast]);

  // NEW: Cancel medical record preview
  const handleCancelMedicalRecord = useCallback(() => {
    setMedicalRecordDraft(null);
    setMedicalRecordPhase("hidden");
    setStatus("idle"); // Reset scan status to idle
  }, []);

  // EXISTING DERIVED DATA FOR UI
  const ocrConfidence = ocrData?.data.ocr_confidence ?? null;
  const qualityDiagnostics = {
    blurScore: ocrData?.data.blur_score ?? null,
    brightness: ocrData?.data.brightness ?? null,
    contrast: ocrData?.data.contrast ?? null,
    isPass: ocrData?.data.is_pass ?? null,
    issues: ocrData?.data.issues ?? [],
  };
  const extractedText = ocrData?.data.extracted_text ?? "";
  const processingTimeMs = ocrData?.data.processing_time_ms ?? 0;
  const matches =
    ocrData?.mode === "composition" ? (ocrData.data as OCRCompositionResponse).result.matches ?? [] : [];
  const compositionCardData =
    ocrData?.mode === "composition"
      ? {
          matches: (ocrData.data as OCRCompositionResponse).result.matches,
          genericMatches: (ocrData.data as OCRCompositionResponse).result.generic_matches ?? [],
        }
      : null;
  const showResults =
    (ocrData !== null && status === "success") ||
    status === "processing";

  // NEW: Render inventory panel when needed
  const showInventoryPanel = inventoryPhase === "preview" || inventoryPhase === "submitting";
  const showSubmissionSummary = inventoryPhase === "complete";

  return (
    <div className="space-y-6">
      <ScannerHeader onResolveDuplicate={handleResolveDuplicate} />

      {/* Hidden file picker */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/png,image/jpeg,image/jpg"
        onChange={(e) => {
          const file = e.target.files[0];
          if (file) handleFileSelect(file);
        }}
        className="hidden"
      />

      {/* Scan options */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {scanOptions.map((opt) => (
          <ScanOptionCard
            key={opt.key}
            {...opt}
            onClick={() => handleScanOption(opt.key)}
          />
        ))}
      </div>

      {/* Image preview */}
      <ImagePreview
        selectedFile={selectedFile}
        previewUrl={previewUrl}
        status={status}
        scanMode={scanMode}
        error={error}
        onFileSelect={handleFileSelect}
        onStartScan={handleStartScan}
        onClear={handleClear}
      />

      {/* OCR results */}
      {showResults && (
        <div className="space-y-4">
          <OCRPreviewCard
            extractedText={extractedText}
            ocrConfidence={ocrConfidence}
            qualityDiagnostics={qualityDiagnostics}
            processingTimeMs={processingTimeMs}
          />
          {scanMode === "composition" && (
            <CompositionCard data={compositionCardData} />
          )}
          {showResults && (
            <div className="space-y-4">
              {/* existing generic matches section */}
            </div>
          )}
        </div>
      )}

      {/* NEW: Inventory panel */}
      {showInventoryPanel && (
        <InventoryPanel
          items={inventoryItems}
          onToggle={handleToggle}
          onSelectAll={handleSelectAll}
          onClearAll={handleClearAll}
          onSubmit={handleSubmitToInventory}
          onSubmitAll={handleSubmitAll}
          isSubmitting={isSubmitting}
          error={error}
        />
      )}

      {/* NEW: Submission summary */}
      {showSubmissionSummary && (
        <SubmissionSummary
          results={submissionResults}
          onViewInventory={() => {
            // Navigate to inventory page
            // ... navigation logic
          }}
          onScanAnother={handleClear}
        />
      )}

      {/* NEW: Medical record preview */}
      {medicalRecordPhase === "preview" && (
        <MedicalRecordPreview
          draft={medicalRecordDraft as MedicalRecordCreateRequest}
          onChange={(field, value) => {
            setMedicalRecordDraft((prev) => ({
              ...prev,
              [field]: value,
            }));
          }}
          onSave={handleSaveMedicalRecord}
          onCancel={handleCancelMedicalRecord}
          isSaving={isSavingMedicalRecord}
          saveError={medicalRecordSaveError}
        />
      )}

      {/* Empty state */}
      {!showResults && status !== "uploading" && status !== "processing" && (
        <EmptyResults />
      )}
    </div>
  );
}