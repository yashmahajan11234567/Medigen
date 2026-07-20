import { useState, useCallback, useRef, useEffect } from "react";
import { Camera, FileImage, Package, Keyboard } from "lucide-react";
import { apiClient } from "@/lib/api-client";
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
  MedicineForInventory,
  SubmissionResultItem,
  MedicalRecordCreateRequest,
  MedicalRecordDocumentCreate,
  MedicalRecordDocumentType,
  ScanQualityDiagnostics,
} from "@/types/api";

import InventoryPanel from "./components/InventoryPanel";
import SubmissionSummary from "./components/SubmissionSummary";

import MedicineChecklistItem from "./components/MedicineChecklistItem";

import { genericFinderService } from "@/services/genericFinder.service";

import { MedicalRecordPreview } from "./components/MedicalRecordPreview";

import { medicalRecordsService } from "@/services/medicalRecords.service";

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

  const [scanMode, setScanMode] = useState<ScanMode>("composition");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string>("");
  const [status, setStatus] = useState<PageStatus>("idle");
  const [error, setError] = useState<string | null>(null);
  const [ocrData, setOcrData] = useState<OcrData | null>(null);

  const [inventoryPhase, setInventoryPhase] = useState<InventoryPhase>("hidden");
  const [inventoryItems, setInventoryItems] = useState<MedicineForInventory[]>([]);
  const [submissionResults, setSubmissionResults] = useState<SubmissionResultItem[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [selectedCount, setSelectedCount] = useState(0);
  const [isLookingUp, setIsLookingUp] = useState<Record<string, boolean>>({});

  const [medicalRecordPhase, setMedicalRecordPhase] = useState<'hidden' | 'preview' | 'saving' | 'complete'>('hidden');
  const [medicalRecordDraft, setMedicalRecordDraft] = useState<MedicalRecordCreateRequest | null>(null);
  const [isSavingMedicalRecord, setIsSavingMedicalRecord] = useState(false);
  const [medicalRecordSaveError, setMedicalRecordSaveError] = useState<string | null>(null);

  const handleResolveDuplicate = useCallback((action: string, item: MedicineForInventory) => {
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

  const buildInventoryItems = useCallback((data: OcrData): MedicineForInventory[] => {
    const items: MedicineForInventory[] = [];

    switch (data.mode) {
      case "composition": {
        (data.data.result.matches || []).forEach(match => {
          items.push({
            id: match.id.toString(),
            medicineId: match.id,
            name: match.name,
            genericName: match.generic_name,
            brandName: match.brand_name,
            type: match.composition.dosage_form as any,
            strength: match.composition.strength,
            dosageUnit: match.composition.unit,
            quantity: null,
            quantityUnit: null,
            expiryDate: null,
            isSelected: true,
            isKnown: true,
            isDuplicate: false,
            existingInventoryItem: null,
            submissionStatus: "pending",
            error: null,
            randomId: "",
          });
        });
        break;
      }
      case "pharmacy-bill": {
        (data.data.result.medicines || []).forEach((medicine, idx) => {
          items.push({
            id: `bill-${idx}`,
            medicineId: null,
            name: medicine.medicine_name,
            genericName: null,
            brandName: null,
            type: "other",
            strength: medicine.strength,
            dosageUnit: medicine.dosage_unit,
            quantity: medicine.quantity || 1,
            quantityUnit: null,
            expiryDate: null,
            isSelected: true,
            isKnown: false,
            isDuplicate: false,
            existingInventoryItem: null,
            submissionStatus: "pending",
            error: null,
            randomId: "",
          });
        });
        break;
      }
      case "document":
        break;
    }

    return items;
  }, []);

  const handleToggle = useCallback((id: string) => {
    setInventoryItems((prev) =>
      prev.map((item) =>
        item.id === id ? { ...item, isSelected: !item.isSelected } : item
      )
    );
    const selected = inventoryItems.filter((i) => i.isSelected);
    setSelectedCount(selected.length);
  }, [inventoryItems]);

  const handleSelectAll = useCallback(() => {
    setInventoryItems((prev) =>
      prev.map((item) => ({ ...item, isSelected: true }))
    );
    setSelectedCount(inventoryItems.length);
  }, [inventoryItems]);

  const handleClearAll = useCallback(() => {
    setInventoryItems((prev) =>
      prev.map((item) => ({ ...item, isSelected: false }))
    );
    setSelectedCount(0);
  }, [inventoryItems]);

  const handleEdit = useCallback((id: string, field: string, value: string) => {
    setInventoryItems((prev) =>
      prev.map((item) =>
        item.id === id ? { ...item, [field]: value } : item
      )
    );
  }, []);

  const handleLookup = useCallback((id: string) => {
    const item = inventoryItems.find((i) => i.id === id);
    if (!item || item.isKnown) return;

    setIsLookingUp((prev) => ({ ...prev, [id]: true }));

    const name = item.name;
    genericFinderService.search(name)
      .then((result) => {
        const matchedMedicine = (result as any).result?.source_medicine;
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
      addToast({ title: 'Error adding item', variant: 'destructive' });
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
          results.push({
            id: item.id,
            medicineName: item.name,
            medicineId: item.medicineId,
            status: "added",
            error: null,
          });
        } else {
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
            id: item.id,
            medicineName: item.name,
            medicineId: item.medicineId,
            status: "added",
            error: null,
            inventoryItemId: response.data.id,
          });
        }
      } catch (err: any) {
        results.push({
          id: item.id,
          medicineName: item.name,
          medicineId: item.medicineId,
          status: "failed",
          error: err.message || "Submission failed",
        });
      }
    }

    setSubmissionResults(results);
    setInventoryPhase("complete");

    const added = results.filter((r) => r.status === "added").length;
    const skipped = results.filter((r) => r.status === "skipped").length;
    const failed = results.filter((r) => r.status === "failed").length;

    addToast({
      title: `${added} added, ${skipped} skipped, ${failed} failed`,
      variant: "success",
    });

    setIsSubmitting(false);
  }, [inventoryItems, addToast, apiClient]);

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
      if (scanMode === "document") {
        setStatus("processing");
        const ocrResult = await ocrService.document(selectedFile);
        const docResult = ocrResult.result;
        const draft: MedicalRecordCreateRequest = {
          title: `${docResult.patient_name ?? 'Unknown Patient'} – ${docResult.document_type}`,
          folder_name: "Inbox",
          hospital_name: docResult.hospital_or_lab ?? null,
          doctor_name: docResult.doctor_name ?? null,
          visit_date: docResult.report_date ?? null,
          diagnosis: docResult.diagnosis_text ?? null,
          notes: docResult.notes ?? null,
          treatment_name: null,
          description: null,
          documents: [
            {
              document_type: docResult.document_type as MedicalRecordDocumentType,
              file_name: docResult.document_type ?? selectedFile.name,
              file_type: selectedFile.type,
              file_size: selectedFile.size,
              storage_path: "",
              upload_date: new Date().toISOString(),
              doctor_name: docResult.doctor_name ?? null,
              hospital_or_clinic: docResult.hospital_or_lab ?? null,
              doctor_specialty: null,
              consultation_date: null,
              follow_up_date: null,
              diagnosis: docResult.diagnosis_text ?? null,
              notes: docResult.notes ?? null,
              ocr_confidence: ocrResult.ocr_confidence ?? null,
              ocr_processed_at: new Date().toISOString(),
              ocr_source: "upload",
              blur_score: null,
              brightness: null,
              contrast: null,
              is_pass: null,
              issues: [],
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
        setStatus("processing");
        if (scanMode === "composition") {
          const result = await ocrService.composition(selectedFile);
          setOcrData({ mode: "composition", data: result });
          const newItems = buildInventoryItems({ mode: "composition", data: result });
          setInventoryItems(newItems);
        } else if (scanMode === "pharmacy-bill") {
          const result = await ocrService.pharmacyBill(selectedFile);
          setOcrData({ mode: "pharmacy-bill", data: result });
          const newItems = buildInventoryItems({ mode: "pharmacy-bill", data: result });
          setInventoryItems(newItems);
        } else {
          throw new Error("Invalid scan mode");
        }
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

  const handleSaveMedicalRecord = useCallback(async () => {
    if (!medicalRecordDraft) return;
    setIsSavingMedicalRecord(true);
    setMedicalRecordSaveError(null);
    try {
      await medicalRecordsService.create(medicalRecordDraft);
      addToast({ title: "Medical record saved", variant: "success" });
      setMedicalRecordDraft(null);
      setMedicalRecordPhase("hidden");
      window.location.href = "/medical-records";
    } catch (err: any) {
      setMedicalRecordSaveError(
        err.response?.data?.message ||
          err.message ||
          "Failed to save medical record"
      );
      addToast({ title: "Error saving record", variant: "destructive" });
    } finally {
      setIsSavingMedicalRecord(false);
    }
  }, [medicalRecordDraft, medicalRecordsService, addToast]);

  const handleCancelMedicalRecord = useCallback(() => {
    setMedicalRecordDraft(null);
    setMedicalRecordPhase("hidden");
    setStatus("idle");
  }, []);

  const qualityDiagnostics: ScanQualityDiagnostics | null = ocrData?.data.quality_diagnostics ?? null;
  const extractedText = "";
  const processingTimeMs = ocrData?.data.processing_time_ms ?? 0;
  const compositionCardData =
    ocrData?.mode === "composition"
      ? { mode: "composition" as const, composition: { ingredient: "", strength: "", unit: "", dosage_form: "", route: "" } }
      : { mode: null as null };
  const showResults =
    (ocrData !== null && status === "success") ||
    status === "processing";

  const showInventoryPanel = inventoryPhase === "preview" || inventoryPhase === "submitting";

  const scanOptions = [
    { key: "composition" as const, label: "Composition", description: "Scan medicine compositions" },
    { key: "pharmacy-bill" as const, label: "Pharmacy Bill", description: "Scan pharmacy bills" },
    { key: "document" as const, label: "Medical Document", description: "Scan medical documents" },
  ];
  const showSubmissionSummary = inventoryPhase === "complete";

  return (
    <div className="space-y-6">
      <ScannerHeader />

      <input
        ref={fileInputRef}
        type="file"
        accept="image/png,image/jpeg,image/jpg"
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) handleFileSelect(file);
        }}
        className="hidden"
      />

      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {scanOptions.map((opt) => (
          <ScanOptionCard
            key={opt.key}
            icon={opt.key === "composition" ? Package : opt.key === "pharmacy-bill" ? FileImage : Keyboard}
            title={opt.label}
            description={opt.description}
            accent={opt.key === "composition" ? "blue" : opt.key === "pharmacy-bill" ? "green" : "purple"}
            onClick={() => handleScanOption(opt.key)}
          />
        ))}
      </div>

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

      {showResults && (
        <div className="space-y-4">
          <OCRPreviewCard
            extractedText={extractedText}
            ocrConfidence={null}
            qualityDiagnostics={qualityDiagnostics}
            processingTimeMs={processingTimeMs}
          />
          {scanMode === "composition" && (
            <CompositionCard data={compositionCardData as any} />
          )}
        </div>
      )}

      {showInventoryPanel && (
        <InventoryPanel
          items={inventoryItems}
          onToggle={handleToggle}
          onSelectAll={handleSelectAll}
          onClearAll={handleClearAll}
          onEdit={handleEdit}
          onLookup={handleLookup}
          onResolveDuplicate={handleResolveDuplicate as any}
          onSubmit={handleSubmitToInventory}
          onSubmitAll={handleSubmitAll}
          isSubmitting={isSubmitting}
          error={error ?? undefined}
        />
      )}

      {showSubmissionSummary && (
        <SubmissionSummary
          results={submissionResults}
          onViewInventory={() => {}}
          onScanAnother={handleClear}
        />
      )}

      {medicalRecordPhase === "preview" && medicalRecordDraft && (
        <MedicalRecordPreview
          draft={medicalRecordDraft}
          onChange={(field, value) => {
            setMedicalRecordDraft((prev) => prev ? { ...prev, [field]: value } : prev);
          }}
          onSave={handleSaveMedicalRecord}
          onCancel={handleCancelMedicalRecord}
          isSaving={isSavingMedicalRecord}
          saveError={medicalRecordSaveError}
        />
      )}

      {!showResults && status !== "uploading" && (
        <EmptyResults />
      )}
    </div>
  );
}