import { useState } from "react";
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
import type { RecordDetails } from "@/pages/medical-records/components/RecordDrawer";

interface DummyRecord {
  title: string;
  hospital: string;
  date: string;
  recordType: "Prescription" | "Medicine Bill" | "Blood Report" | "Doctor Notes";
  doctorName: string;
  visitDate: string;
  uploadDate: string;
  fileSize: string;
  category: string;
  notes: string;
}

const dummyRecords: DummyRecord[] = [
  { title: "General Checkup", hospital: "City Hospital", date: "12 Mar 2026", recordType: "Prescription", doctorName: "Dr. Sharma", visitDate: "12 Jul 2026", uploadDate: "15 Jul 2026", fileSize: "2.3 MB", category: "General", notes: "Annual health checkup. All vitals normal. Recommended Vitamin D supplements." },
  { title: "Blood Test Results", hospital: "MediLab", date: "28 Feb 2026", recordType: "Blood Report", doctorName: "Dr. Verma", visitDate: "28 Feb 2026", uploadDate: "01 Mar 2026", fileSize: "1.8 MB", category: "General", notes: "Complete blood count and lipid profile. Cholesterol levels slightly elevated." },
  { title: "Pharmacy Receipt", hospital: "HealthPlus Pharmacy", date: "15 Jan 2026", recordType: "Medicine Bill", doctorName: "—", visitDate: "15 Jan 2026", uploadDate: "15 Jan 2026", fileSize: "0.4 MB", category: "General", notes: "Monthly medicine purchase." },
  { title: "Consultation Notes", hospital: "Apollo Clinic", date: "05 Jan 2026", recordType: "Doctor Notes", doctorName: "Dr. Gupta", visitDate: "05 Jan 2026", uploadDate: "06 Jan 2026", fileSize: "0.9 MB", category: "General", notes: "Patient complained of mild fever and body ache. Prescribed rest and paracetamol." },
  { title: "Fever Treatment", hospital: "City Hospital", date: "20 Dec 2025", recordType: "Prescription", doctorName: "Dr. Sharma", visitDate: "20 Dec 2025", uploadDate: "21 Dec 2025", fileSize: "1.2 MB", category: "Fever", notes: "Viral fever. Antibiotics and antipyretics prescribed for 5 days." },
  { title: "Lipid Profile", hospital: "Diagnostic Centre", date: "10 Dec 2025", recordType: "Blood Report", doctorName: "Dr. Mehta", visitDate: "10 Dec 2025", uploadDate: "12 Dec 2025", fileSize: "1.5 MB", category: "Heart", notes: "Lipid profile shows high LDL. Dietary changes recommended." },
  { title: "Dental Checkup", hospital: "Smile Dental", date: "02 Dec 2025", recordType: "Doctor Notes", doctorName: "Dr. Patel", visitDate: "02 Dec 2025", uploadDate: "02 Dec 2025", fileSize: "0.7 MB", category: "Dental", notes: "Routine dental examination. Minor plaque buildup. Teeth cleaning performed." },
  { title: "Monthly Medication", hospital: "Wellness Pharmacy", date: "28 Nov 2025", recordType: "Medicine Bill", doctorName: "—", visitDate: "28 Nov 2025", uploadDate: "28 Nov 2025", fileSize: "0.3 MB", category: "General", notes: "Monthly refill of prescribed medications." },
];

export function MedicalRecordsPage() {
  const [view, setView] = useState<"gallery" | "list">("gallery");
  const [sortBy, setSortBy] = useState("Disease");
  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [selectedRecord, setSelectedRecord] = useState<RecordDetails | null>(null);

  const openDrawer = (record: DummyRecord) => {
    setSelectedRecord({
      title: record.title,
      documentType: record.recordType,
      hospital: record.hospital,
      doctorName: record.doctorName,
      visitDate: record.visitDate,
      uploadDate: record.uploadDate,
      fileSize: record.fileSize,
      category: record.category,
      notes: record.notes,
    });
    setDrawerOpen(true);
  };

  const closeDrawer = () => {
    setDrawerOpen(false);
  };

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
        {dummyRecords.length === 0 ? (
          <EmptyRecords />
        ) : view === "gallery" ? (
          <div className="grid grid-cols-2 gap-3 pb-20 sm:grid-cols-3 md:grid-cols-4">
            {dummyRecords.map((r) => (
              <RecordCard
                key={r.title}
                title={r.title}
                hospital={r.hospital}
                date={r.date}
                recordType={r.recordType}
                onClick={() => openDrawer(r)}
              />
            ))}
          </div>
        ) : (
          <div className="pb-20">
            <RecordList
              records={dummyRecords}
              onRecordClick={(i) => openDrawer(dummyRecords[i])}
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