import { useEffect, useState } from "react";
import { useMedicalRecords } from "@/hooks/useMedicalRecords";
import { RecordsHeader } from "@/pages/medical-records/components/RecordsHeader";
import { RecordsSearch } from "@/pages/medical-records/components/RecordsSearch";
import { ViewToggle } from "@/pages/medical-records/components/ViewToggle";
import { SortDropdown } from "@/pages/medical-records/components/SortDropdown";
import { FolderGrid } from "@/pages/medical-records/components/FolderGrid";
import { RecordCard } from "@/pages/medical-records/components/RecordCard";
import { RecordList } from "@/pages/medical-records/components/RecordList";
import { EmptyRecords } from "@/pages/medical-records/components/EmptyRecords";
import { UploadButton } from "@/pages/medical-records/components/UploadButton";
import { UploadModal } from "@/pages/medical-records/components/UploadModal";
import { RecordDrawer } from "@/pages/medical-records/components/RecordDrawer";
import { LoadingScreen } from "@/components/common/LoadingScreen";
import { InlineError } from "@/components/feedback/InlineError";
import type { RecordDetails } from "@/pages/medical-records/components/RecordDrawer";
import type { MedicalRecordResponse } from "@/types/api";

const recordTypes = ["Prescription", "Medicine Bill", "Blood Report", "Doctor Notes"] as const;
type RecordType = (typeof recordTypes)[number];

function mapDocumentType(type: string): RecordType {
  const normalized = type.toLowerCase();
  if (normalized === "prescription") return "Prescription";
  if (normalized === "pharmacy_bill") return "Medicine Bill";
  if (normalized === "blood_report" || normalized === "lab_report") return "Blood Report";
  if (normalized === "doctor_note") return "Doctor Notes";
  return "Prescription";
}

function formatDate(dateStr: string | null): string {
  if (!dateStr) return "—";
  try {
    const date = new Date(dateStr);
    return date.toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" });
  } catch {
    return dateStr;
  }
}

function formatDateTime(dateStr: string | null): string {
  if (!dateStr) return "—";
  try {
    const date = new Date(dateStr);
    return date.toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" });
  } catch {
    return dateStr;
  }
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function convertToRecordCardData(record: MedicalRecordResponse) {
  const firstDoc = record.documents[0];
  const docType = firstDoc ? mapDocumentType(firstDoc.document_type) : "Prescription";

  return {
    title: record.title,
    hospital: record.hospital_name || "Unknown Hospital",
    date: formatDate(record.visit_date),
    recordType: docType,
    id: record.id,
  };
}

function convertToRecordListRow(record: MedicalRecordResponse) {
  const firstDoc = record.documents[0];
  const docType = firstDoc ? mapDocumentType(firstDoc.document_type) : "Prescription";

  return {
    title: record.title,
    hospital: record.hospital_name || "Unknown Hospital",
    date: formatDate(record.visit_date),
    recordType: docType,
  };
}

function convertToRecordDetails(record: MedicalRecordResponse): RecordDetails {
  const firstDoc = record.documents[0];
  const docType = firstDoc ? mapDocumentType(firstDoc.document_type) : "Prescription";

  return {
    title: record.title,
    documentType: docType,
    hospital: record.hospital_name || "Unknown Hospital",
    doctorName: record.doctor_name || "—",
    visitDate: formatDate(record.visit_date),
    uploadDate: firstDoc ? formatDateTime(firstDoc.upload_date) : "—",
    fileSize: firstDoc ? formatFileSize(firstDoc.file_size) : "—",
    category: record.folder_name || "General",
    notes: record.notes || "",
  };
}

export function MedicalRecordsPage() {
  const {
    records,
    loading,
    error,
    fetchRecords,
  } = useMedicalRecords();

  const [view, setView] = useState<"gallery" | "list">("gallery");
  const [sortBy, setSortBy] = useState("Disease");
  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [selectedRecord, setSelectedRecord] = useState<RecordDetails | null>(null);

  useEffect(() => {
    fetchRecords();
  }, [fetchRecords]);

  const openDrawer = (record: MedicalRecordResponse) => {
    setSelectedRecord(convertToRecordDetails(record));
    setDrawerOpen(true);
  };

  const closeDrawer = () => {
    setDrawerOpen(false);
  };

  const cardRecords = records.map(convertToRecordCardData);
  const listRecords = records.map(convertToRecordListRow);

  return (
    <div className="space-y-6">
      <RecordsHeader />
      <RecordsSearch />

      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <ViewToggle view={view} onChange={setView} />
        <div className="w-full sm:w-48">
          <SortDropdown value={sortBy} onChange={setSortBy} />
        </div>
      </div>

      <div>
        <div className="mb-3 flex items-center gap-3">
          <div className="h-1 w-8 rounded-full bg-brand-500" />
          <h2 className="text-lg font-semibold text-slate-900">Categories</h2>
        </div>
        <FolderGrid />
      </div>

      <div>
        <div className="mb-3 flex items-center gap-3">
          <div className="h-1 w-8 rounded-full bg-brand-500" />
          <h2 className="text-lg font-semibold text-slate-900">All Records</h2>
        </div>

        {loading && records.length === 0 && (
          <LoadingScreen
            title="Loading records…"
            description="Please wait while we fetch your medical records."
          />
        )}

        {error && !loading && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-800">
            <InlineError title="Failed to load records" message={error} />
          </div>
        )}

        {!loading && !error && records.length === 0 && (
          <EmptyRecords />
        )}

        {!loading && !error && records.length > 0 && view === "gallery" && (
          <div className="grid grid-cols-2 gap-3 pb-20 sm:grid-cols-3 md:grid-cols-4">
            {records.map((record) => {
              const cardData = convertToRecordCardData(record);
              return (
                <RecordCard
                  key={record.id}
                  title={cardData.title}
                  hospital={cardData.hospital}
                  date={cardData.date}
                  recordType={cardData.recordType}
                  onClick={() => openDrawer(record)}
                />
              );
            })}
          </div>
        )}

        {!loading && !error && records.length > 0 && view === "list" && (
          <div className="pb-20">
            <RecordList
              records={listRecords}
              onRecordClick={(i) => openDrawer(records[i])}
            />
          </div>
        )}
      </div>

      <UploadButton onClick={() => setUploadModalOpen(true)} />
      <UploadModal open={uploadModalOpen} onClose={() => setUploadModalOpen(false)} />
      <RecordDrawer open={drawerOpen} record={selectedRecord} onClose={closeDrawer} />
    </div>
  );
}