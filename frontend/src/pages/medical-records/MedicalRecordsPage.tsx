import { useState } from "react";
import { PageIntro } from "@/components/common/PageIntro";
import { Input } from "@/components/common/Input";
import { Button } from "@/components/common/Button";
import { Card } from "@/components/common/Card";
import { EmptyState } from "@/components/common/EmptyState";
import { LoadingScreen } from "@/components/common/LoadingScreen";
import { InlineError } from "@/components/feedback/InlineError";
import { useMedicalRecords } from "@/hooks/useMedicalRecords";
import { Calendar, Folder, Plus, Search } from "lucide-react";
import type {
  MedicalRecordCreateRequest,
  MedicalRecordUpdateRequest,
  MedicalRecordResponse,
} from "@/types/api";

// Simple TextArea component since it doesn't exist in the common components
const TextArea = ({
  id,
  name,
  value,
  onChange,
  rows = 2,
}: {
  id: string;
  name: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
  rows?: number;
}) => (
  <textarea
    id={id}
    name={name}
    value={value}
    onChange={onChange}
    rows={rows}
    className="block w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm ring-default placeholder:text-muted-foreground focus:border-primary focus:ring-primary focus:ring-offset-0 disabled:opacity-50 disabled:pointer-events-none"
  />
);

// Simple Label component since it doesn't exist in the common components
const Label = ({ htmlFor, children }: { htmlFor: string; children: React.ReactNode }) => (
  <label htmlFor={htmlFor} className="mb-2 text-sm font-medium text-muted-foreground block">
    {children}
  </label>
);

export function MedicalRecordsPage() {
  const {
    records,
    loading: recordsLoading,
    error: recordsError,
    fetchRecords,
    searchRecords,
    createRecord,
    updateRecord,
    deleteRecord,
  } = useMedicalRecords();

  const [searchQuery, setSearchQuery] = useState("");
  const [formData, setFormData] = useState<MedicalRecordCreateRequest>({
    title: "",
    folder_name: "",
    description: null,
    hospital_name: null,
    doctor_name: null,
    visit_date: null,
    diagnosis: null,
    treatment_name: null,
    notes: null,
    // We'll initialize the complex fields as empty arrays
    documents: [],
    linked_schedule_ids: [],
    linked_inventory_item_ids: [],
    linked_medicine_ids: [],
    linked_generic_search_ids: [],
  });
  const [editMode, setEditMode] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [formLoading, setFormLoading] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const [formSuccess, setFormSuccess] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
  };

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      searchRecords(searchQuery);
    } else {
      fetchRecords();
    }
  };

  const handleFormChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value, type } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]:
        type === "checkbox"
          ? (e.target as HTMLInputElement).checked
          : type === "number"
            ? value === ""
              ? null
              : Number(value)
            : value,
    }));
  };

  const handleDateChange = (
    field: "visit_date" | "hospital_name" | "doctor_name" | "diagnosis" | "treatment_name" | "notes",
    value: string
  ) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value === "" ? null : value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormLoading(true);
    setFormError(null);
    setFormSuccess(null);
    try {
      if (editMode && editingId !== null) {
        await updateRecord(
          editingId,
          formData as unknown as MedicalRecordUpdateRequest
        );
        setFormSuccess("Record updated successfully");
        setTimeout(() => {
          setFormSuccess(null);
        }, 3000);
        // Reset form and hide
        setEditMode(false);
        setEditingId(null);
        setFormData({
          title: "",
          folder_name: "",
          description: null,
          hospital_name: null,
          doctor_name: null,
          visit_date: null,
          diagnosis: null,
          treatment_name: null,
          notes: null,
          documents: [],
          linked_schedule_ids: [],
          linked_inventory_item_ids: [],
          linked_medicine_ids: [],
          linked_generic_search_ids: [],
        });
        setShowForm(false);
        // Refetch list
        await fetchRecords();
      } else {
        await createRecord(formData);
        setFormSuccess("Record created successfully");
        setTimeout(() => {
          setFormSuccess(null);
        }, 3000);
        // Reset form
        setFormData({
          title: "",
          folder_name: "",
          description: null,
          hospital_name: null,
          doctor_name: null,
          visit_date: null,
          diagnosis: null,
          treatment_name: null,
          notes: null,
          documents: [],
          linked_schedule_ids: [],
          linked_inventory_item_ids: [],
          linked_medicine_ids: [],
          linked_generic_search_ids: [],
        });
        setShowForm(false);
        // Refetch list
        await fetchRecords();
      }
    } catch (err: any) {
      const message =
        err.response?.data?.message ||
        err.message ||
        "Failed to save medical record";
      setFormError(message);
    } finally {
      setFormLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm("Are you sure you want to delete this medical record?")) {
      return;
    }
    try {
      await deleteRecord(id);
      // Refetch list
      await fetchRecords();
    } catch (err: any) {
      alert("Failed to delete record: " + (err.response?.data?.message || err.message));
    }
  };

  const handleEdit = (record: MedicalRecordResponse) => {
    setEditMode(true);
    setEditingId(record.id);
    setFormData({
      title: record.title,
      folder_name: record.folder_name,
      description: record.description ?? null,
      hospital_name: record.hospital_name ?? null,
      doctor_name: record.doctor_name ?? null,
      visit_date: record.visit_date ?? null,
      diagnosis: record.diagnosis ?? null,
      treatment_name: record.treatment_name ?? null,
      notes: record.notes ?? null,
      // We are not loading the complex fields for edit simplicity; in a real app we would.
      documents: [],
      linked_schedule_ids: [],
      linked_inventory_item_ids: [],
      linked_medicine_ids: [],
      linked_generic_search_ids: [],
    });
    setShowForm(true);
  };

  return (
    <>
      <PageIntro
        eyebrow="Medical Records"
        title="Medical Records Management"
        description="View, search, filter, and manage your medical records."
      />
      {recordsError && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-800">
          <InlineError title="Error" message={recordsError} />
        </div>
      )}
      <div className="space-y-6">
        {/* Add Record Form */}
        {showForm && (
          <Card className="mb-4">
            <div className="flex justify-between items-start mb-4">
              <h2 className="text-lg font-semibold">
                {editMode ? "Edit Medical Record" : "New Medical Record"}
              </h2>
              <Button variant="secondary" size="sm" onClick={() => {
                setShowForm(false);
                setEditMode(false);
                setEditingId(null);
                setFormData({
                  title: "",
                  folder_name: "",
                  description: null,
                  hospital_name: null,
                  doctor_name: null,
                  visit_date: null,
                  diagnosis: null,
                  treatment_name: null,
                  notes: null,
                  documents: [],
                  linked_schedule_ids: [],
                  linked_inventory_item_ids: [],
                  linked_medicine_ids: [],
                  linked_generic_search_ids: [],
                });
              }}>
                <span className="mr-2">×</span>
              </Button>
            </div>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div>
                  <Label htmlFor="title">Title *</Label>
                  <Input
                    label="Title"
                    id="title"
                    name="title"
                    value={formData.title}
                    onChange={handleFormChange}
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="folder_name">Folder *</Label>
                  <Input
                    label="Folder"
                    id="folder_name"
                    name="folder_name"
                    value={formData.folder_name}
                    onChange={handleFormChange}
                    required
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="description">Description</Label>
                <TextArea
                  id="description"
                  name="description"
                  value={formData.description || ""}
                  onChange={handleFormChange}
                  rows={3}
                />
              </div>

              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div>
                  <Label htmlFor="hospital_name">Hospital</Label>
                  <Input
                    label="Hospital"
                    id="hospital_name"
                    name="hospital_name"
                    value={formData.hospital_name || ""}
                    onChange={handleFormChange}
                  />
                </div>
                <div>
                  <Label htmlFor="doctor_name">Doctor</Label>
                  <Input
                    label="Doctor"
                    id="doctor_name"
                    name="doctor_name"
                    value={formData.doctor_name || ""}
                    onChange={handleFormChange}
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div>
                  <Label htmlFor="visit_date">Visit Date</Label>
                  <Input
                    label="Visit Date"
                    id="visit_date"
                    name="visit_date"
                    type="date"
                    value={formData.visit_date || ""}
                    onChange={(e) => handleDateChange("visit_date", e.target.value)}
                  />
                </div>
                <div>
                  <Label htmlFor="diagnosis">Diagnosis</Label>
                  <Input
                    label="Diagnosis"
                    id="diagnosis"
                    name="diagnosis"
                    value={formData.diagnosis || ""}
                    onChange={handleFormChange}
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div>
                  <Label htmlFor="treatment_name">Treatment</Label>
                  <Input
                    label="Treatment"
                    id="treatment_name"
                    name="treatment_name"
                    value={formData.treatment_name || ""}
                    onChange={handleFormChange}
                  />
                </div>
                <div>
                  <Label htmlFor="notes">Notes</Label>
                  <TextArea
                    id="notes"
                    name="notes"
                    value={formData.notes || ""}
                    onChange={handleFormChange}
                    rows={3}
                  />
                </div>
              </div>

              {/* Form Status Messages */}
              {formError && (
                <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-800">
                  <InlineError title="Error" message={formError} />
                </div>
              )}
              {formSuccess && (
                <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg text-green-800">
                  <InlineError title="Success" message={formSuccess} />
                </div>
              )}

              <div className="flex justify-end space-x-3">
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => {
                    setShowForm(false);
                    setEditMode(false);
                    setEditingId(null);
                    setFormData({
                      title: "",
                      folder_name: "",
                      description: null,
                      hospital_name: null,
                      doctor_name: null,
                      visit_date: null,
                      diagnosis: null,
                      treatment_name: null,
                      notes: null,
                      documents: [],
                      linked_schedule_ids: [],
                      linked_inventory_item_ids: [],
                      linked_medicine_ids: [],
                      linked_generic_search_ids: [],
                    });
                  }}
                >
                  Cancel
                </Button>
                <Button
                  variant="primary"
                  size="sm"
                  type="submit"
                  disabled={formLoading}
                >
                  {formLoading ? "Saving..." : (editMode ? "Update" : "Create")}
                </Button>
              </div>
            </form>
          </Card>
        )}

        <div className="flex justify-between items-center wrap gap-3">
          <div className="flex flex-col sm:flex-row items-center gap-2">
            <Input
              label="Search"
              placeholder="Search records by title, folder, or description..."
              value={searchQuery}
              onChange={handleSearchChange}
              className="w-full max-w-sm"
            />
            <Button variant="secondary" size="sm" onClick={handleSearchSubmit}>
              <Search className="mr-2" /> Search
            </Button>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="primary"
              size="sm"
              onClick={() => {
                setShowForm(true);
                setEditMode(false);
                setEditingId(null);
                setFormData({
                  title: "",
                  folder_name: "",
                  description: null,
                  hospital_name: null,
                  doctor_name: null,
                  visit_date: null,
                  diagnosis: null,
                  treatment_name: null,
                  notes: null,
                  documents: [],
                  linked_schedule_ids: [],
                  linked_inventory_item_ids: [],
                  linked_medicine_ids: [],
                  linked_generic_search_ids: [],
                });
              }}
            >
              <Plus className="mr-2" /> New Record
            </Button>
          </div>
        </div>

        <Card>
          <div className="flex justify-between items-start mb-4">
            <h2 className="text-lg font-semibold">
              Medical Records ({records.length})
            </h2>
          </div>
          {recordsLoading && records.length === 0 ? (
            <LoadingScreen
              title="Loading records…"
              description="Please wait while we load your medical records."
            />
          ) : recordsError ? (
            <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-800">
              <InlineError title="Load error" message={recordsError} />
            </div>
          ) : records.length === 0 ? (
            <EmptyState
              icon={Folder}
              title="No medical records yet"
              description="Add your first medical record using the button above."
            />
          ) : (
            <div className="space-y-4">
              {records.map((record) => (
                <div
                  key={record.id}
                  className="p-4 bg-slate-50 border border-slate-200 rounded-lg"
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="font-medium text-slate-900">
                        {record.title}
                      </h3>
                      <p className="text-sm text-slate-600">
                        <Folder className="mr-1 h-4 w-4" /> {record.folder_name}
                      </p>
                      {record.description && (
                        <p className="text-sm text-slate-600 line-clamp-2">
                          {record.description}
                        </p>
                      )}
                      {record.hospital_name && (
                        <p className="text-sm text-slate-600">
                          <Search className="mr-1 h-4 w-4" /> {record.hospital_name}
                        </p>
                      )}
                      {record.doctor_name && (
                        <p className="text-sm text-slate-600">
                          <Search className="mr-1 h-4 w-4" /> {record.doctor_name}
                        </p>
                      )}
                      {record.visit_date && (
                        <p className="text-sm text-slate-600">
                          <Calendar className="mr-1 h-4 w-4" />{" "}
                            {new Date(record.visit_date).toLocaleDateString()}
                        </p>
                      )}
                      {record.diagnosis && (
                        <p className="text-sm text-slate-600 italic">
                          {record.diagnosis}
                        </p>
                      )}
                      {record.treatment_name && (
                        <p className="text-sm text-slate-600">
                          {record.treatment_name}
                        </p>
                      )}
                      {record.notes && (
                        <p className="text-sm text-slate-600 italic">
                          {record.notes}
                        </p>
                      )}
                    </div>
                    <div className="text-xs text-slate-500">
                      <span>Status: Active</span>
                    </div>
                  </div>
                  <div className="mt-3 flex justify-end space-x-2">
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={() => handleEdit(record)}
                    >
                      Edit
                    </Button>
                    <Button
                      variant="danger"
                      size="sm"
                      onClick={() => handleDelete(record.id)}
                    >
                      Delete
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>
      </div>
    </>
  );
}