import { useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/common/Card";
import { SectionTitle } from "@/pages/dashboard/components/SectionTitle";
import { Input } from "@/components/common/Input";
import { Textarea } from "@/components/common/Textarea";
import { Select } from "@/components/common/Select";
import { DatePicker } from "@/components/common/DatePicker";
import { Button } from "@/components/common/Button";
import { PreviewPlaceholder } from "@/pages/medical-records/components/PreviewPlaceholder";
import { QualityBadge } from "./QualityBadge";
import type { MedicalRecordCreateRequest, MedicalRecordDocumentCreate } from "@/types/api";

interface MedicalRecordPreviewProps {
  draft: MedicalRecordCreateRequest;
  onChange: (field: keyof MedicalRecordCreateRequest, value: any) => void;
  onSave: () => void;
  onCancel: () => void;
  isSaving: boolean;
  saveError: string | null;
}

export function MedicalRecordPreview({
  draft,
  onChange,
  onSave,
  onCancel,
  isSaving,
  saveError,
}: MedicalRecordPreviewProps) {
  const [title, setTitle] = useState(draft.title);
  const [folderName, setFolderName] = useState(draft.folder_name);
  const [doctorName, setDoctorName] = useState(draft.doctor_name ?? "");
  const [hospitalName, setHospitalName] = useState(draft.hospital_name ?? "");
  const [visitDate, setVisitDate] = useState(draft.visit_date ?? "");
  const [diagnosis, setDiagnosis] = useState(draft.diagnosis ?? "");
  const [notes, setNotes] = useState(draft.notes ?? "");

  // Handle changes
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    switch (name) {
      case "title":
        setTitle(value);
        onChange("title", value);
        break;
      case "folder_name":
        setFolderName(value);
        onChange("folder_name", value);
        break;
      case "doctor_name":
        setDoctorName(value);
        onChange("doctor_name", value === "" ? null : value);
        break;
      case "hospital_name":
        setHospitalName(value);
        onChange("hospital_name", value === "" ? null : value);
        break;
      case "visit_date":
        setVisitDate(value);
        onChange("visit_date", value === "" ? null : value);
        break;
      case "diagnosis":
        setDiagnosis(value);
        onChange("diagnosis", value === "" ? null : value);
        break;
      case "notes":
        setNotes(value);
        onChange("notes", value === "" ? null : value);
        break;
      default:
        break;
    }
  };

  return (
    <Card className="p-5 sm:p-6">
      <SectionTitle>Medical Record Preview</SectionTitle>

      {saveError && (
        <div className="mb-4 p-3 bg-red-50 text-red-700 rounded">
          {saveError}
        </div>
      )}

      <div className="mb-5 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-slate-900">Record Details</h2>
        <Button
          variant="outline"
          size="sm"
          onClick={onCancel}
          disabled={isSaving}
        >
          Cancel
        </Button>
      </div>


      <div className="space-y-5">
        <div className="space-y-5">
          <label className="mb-1.5 block text-sm font-medium text-slate-700">Title</label>
          <Input
            name="title"
            value={title}
            onChange={handleChange}
            placeholder="Enter title"
            className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 placeholder-slate-400 shadow-soft transition focus:border-brand-300 focus:outline-none focus:ring-4 focus:ring-brand-100"
          />
        </div>

        <div>
          <label className="mb-1.5 block text-sm font-medium text-slate-700">Folder</label>
          <Input
            name="folder_name"
            value={folderName}
            onChange={handleChange}
            placeholder="Enter folder name (e.g., Inbox)"
            className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 placeholder-slate-400 shadow-soft transition focus:border-brand-300 focus:outline-none focus:ring-4 focus:ring-brand-100"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="mb-1.5 block text-sm font-medium text-slate-700">Doctor Name</label>
            <Input
              name="doctor_name"
              value={doctorName}
              onChange={handleChange}
              placeholder="Enter doctor name"
              className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 placeholder-slate-400 shadow-soft transition focus:border-brand-300 focus:outline-none focus:ring-4 focus:ring-brand-100"
            />
          </div>
          <div>
            <label className="mb-1.5 block text-sm font-medium text-slate-700">Hospital / Clinic</label>
            <Input
              name="hospital_name"
              value={hospitalName}
              onChange={handleChange}
              placeholder="Enter hospital or clinic name"
              className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 placeholder-slate-400 shadow-soft transition focus:border-brand-300 focus:outline-none focus:ring-4 focus:ring-brand-100"
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="mb-1.5 block text-sm font-medium text-slate-700">Visit Date</label>
            <DatePicker
              name="visit_date"
              value={visitDate}
              onChange={(value) => handleChange({ target: { name: "visit_date", value: value ?? "" } } as React.ChangeEvent<HTMLInputElement>)}
              className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 placeholder-slate-400 shadow-soft transition focus:border-brand-300 focus:outline-none focus:ring-4 focus:ring-brand-100"
            />
          </div>
          <div>
            <label className="mb-1.5 block text-sm font-medium text-slate-700">Diagnosis</label>
            <Input
              name="diagnosis"
              value={diagnosis}
              onChange={handleChange}
              placeholder="Enter diagnosis (if any)"
              className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 placeholder-slate-400 shadow-soft transition focus:border-brand-300 focus:outline-none focus:ring-4 focus:ring-brand-100"
            />
          </div>
        </div>

        <div>
          <label className="mb-1.5 block text-sm font-medium text-slate-700">Notes</label>
          <Textarea
            name="notes"
            value={notes}
            onChange={handleChange}
            placeholder="Enter additional notes"
            className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 placeholder-slate-400 shadow-soft transition focus:border-brand-300 focus:outline-none focus:ring-4 focus:ring-brand-100"
          />
        </div>

        {/* Document Section */}
        <div className="space-y-4">
          <div className="flex items-center gap-3">
            <div className="h-1 w-8 rounded-full bg-brand-500" />
            <h2 className="text-lg font-semibold text-slate-900">Attached Document</h2>
          </div>

          <div className="space-y-3">
            <PreviewPlaceholder type="image" className="h-40 w-full object-cover rounded-2xl" />
            <div className="space-y-2">
              <QualityBadge
                confidence={draft.documents?.[0]?.ocr_confidence ?? null}
                blurScore={draft.documents?.[0]?.blur_score ?? null}
                brightness={draft.documents?.[0]?.brightness ?? null}
                contrast={draft.documents?.[0]?.contrast ?? null}
                isPass={draft.documents?.[0]?.is_pass ?? null}
                issues={draft.documents?.[0]?.issues ?? []}
              />
            </div>
          </div>
        </div>

        <div className="flex items-center justify-end">
          <Button
            variant="solid"
            size="lg"
            onClick={onSave}
            disabled={isSaving || !title.trim() || !folderName.trim()}
            className="w-full md:w-auto"
          >
            {isSaving ? "Saving..." : "Save Record"}
          </Button>
        </div>
      </div>
    </Card>
  );
}