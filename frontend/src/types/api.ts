export interface ApiErrorPayload {
  message: string;
  code: string;
  details?: Array<Record<string, unknown>>;
}

export interface User {
  id: number;
  full_name: string;
  email: string;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  updated_at: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  full_name: string;
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface DashboardUserSummary {
  id: number;
  name: string;
}

export interface DashboardScheduleItem {
  id: number;
  medicine_id: number;
  medicine_name: string;
  dosage_amount: string | null;
  dosage_unit: string | null;
  frequency: string | null;
  reminder_time: string | null;
}

export interface DashboardInventorySummary {
  total_medicines: number;
  expiring_soon: number;
}

export interface DashboardResponse {
  user: DashboardUserSummary;
  greeting: string;
  notification_count: number;
  today_schedule: DashboardScheduleItem[];
  inventory_summary: DashboardInventorySummary;
}

// Generic Finder types
export interface CanonicalComposition {
  ingredient: string;
  strength: string;
  unit: string;
  dosage_form: number; // MedicineType enum as number
  route: string;
}

export interface GenericMedicineSummary {
  id: number;
  name: string;
  generic_name: string | null;
  brand_name: string | null;
  composition: CanonicalComposition;
}

export interface GenericFinderSearchResponse {
  source_medicine: GenericMedicineSummary | null;
  normalized_composition: CanonicalComposition;
  matches: GenericMedicineSummary[];
  message: string;
}

export interface GenericMedicineDetailResponse {
  medicine: GenericMedicineSummary;
  is_generic: boolean;
}

// OCR types
export interface ScanQualityDiagnostics {
  issues: string[];
  blur_score: number | null;
  brightness: number | null;
  contrast: number | null;
  is_pass: boolean;
}

export interface MedicineEntry {
  medicine_name: string;
  strength: string | null;
  dosage_unit: string | null;
  quantity: number | null;
}

export interface BillParseResult {
  medicines: MedicineEntry[];
  raw_text: string;
}

export interface DocumentParseResult {
  document_type: string;
  patient_name: string | null;
  doctor_name: string | null;
  hospital_or_lab: string | null;
  report_date: string | null;
  medicines: MedicineEntry[];
  diagnosis_text: string | null;
  notes: string | null;
  raw_text: string;
}

export interface OCRCompositionResponse {
  ocr_confidence: number | null;
  quality_diagnostics: ScanQualityDiagnostics | null;
  processing_time_ms: number;
  result: GenericFinderSearchResponse;
}

export interface OCRPharmacyBillResponse {
  ocr_confidence: number | null;
  quality_diagnostics: ScanQualityDiagnostics | null;
  processing_time_ms: number;
  result: BillParseResult;
}

export interface OCRDocumentResponse {
  ocr_confidence: number | null;
  quality_diagnostics: ScanQualityDiagnostics | null;
  processing_time_ms: number;
  result: DocumentParseResult;
}

export interface AddToInventoryRequest {
  medicine_id: number;
  quantity: number | null;
  quantity_unit: string | null;
  expiry_date: string | null; // ISO date string
}

export interface AddToInventoryResponse {
  message: string;
  medicine_id: number;
}

// Inventory types
export type MedicineType =
  | "tablet"
  | "capsule"
  | "syrup"
  | "cream"
  | "injection"
  | "ointment"
  | "drops"
  | "inhaler"
  | "other";

export type InventoryStatus =
  | "available"
  | "low_stock"
  | "expiring_soon"
  | "expired"
  | "out_of_stock";

export interface InventoryResponseItem {
  id: number;
  medicine_id: number;
  name: string;
  generic_name: string | null;
  brand_name: string | null;
  type: MedicineType;
  quantity: number | null;
  quantity_unit: string | null;
  status: InventoryStatus;
  expiry_date: string | null; // ISO date string
  purchase_date: string | null; // ISO date string
  image_path: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface InventoryListResponse {
  items: InventoryResponseItem[];
}

export interface InventorySummaryResponse {
  total_medicines: number;
  available_medicines: number;
  finished_medicines: number;
  expiring_soon: number;
  expired: number;
}

export interface InventoryCreateRequest {
  medicine_id: number | null;
  name: string | null;
  generic_name: string | null;
  brand_name: string | null;
  type: MedicineType;
  quantity: number | null;
  quantity_unit: string | null;
  expiry_date: string | null; // ISO date string
  purchase_date: string | null; // ISO date string
  image_path: string | null;
  notes: string | null;
}

export interface InventoryUpdateRequest {
  name: string | null;
  generic_name: string | null;
  brand_name: string | null;
  type: MedicineType | null;
  quantity: number | null;
  quantity_unit: string | null;
  expiry_date: string | null; // ISO date string
  purchase_date: string | null; // ISO date string
  image_path: string | null;
  notes: string | null;
}

export interface InventoryDeleteResponse {
  message: string;
}

// Scheduler types
export interface ReminderTimesInput {
  morning: string | null; // HH:MM format as string
  afternoon: string | null;
  night: string | null;
}

export interface ScheduleBaseRequest {
  medicine_id: number;
  dosage_pattern: string; // e.g., "1-0-1"
  food_timing: string; // "before_food" | "after_food"
  start_date: string; // ISO date
  end_date: string | null;
  duration_days: number | null;
  reminder_times: ReminderTimesInput | null;
  notes: string | null;
  quantity: number | null;
  quantity_unit: string | null;
  purchase_date: string | null;
  expiry_date: string | null;
  pharmacy_name: string | null;
}

export interface ScheduleCreateRequest extends ScheduleBaseRequest {
  source: string; // "manual" | "pharmacy_bill" | "generic_finder"
}

export interface ScheduleUpdateRequest {
  dosage_pattern?: string;
  food_timing?: string;
  start_date?: string;
  end_date?: string;
  duration_days?: number;
  reminder_times?: ReminderTimesInput | null;
  notes?: string | null;
  quantity?: number | null;
  quantity_unit?: string | null;
  purchase_date?: string | null;
  expiry_date?: string | null;
  pharmacy_name?: string | null;
  status?: string; // "active" | "paused" | "completed" | "cancelled"
}

export interface BillMedicineInput {
  medicine_name: string;
  quantity: number | null;
  purchase_date: string | null;
  expiry_date: string | null;
  pharmacy_name: string | null;
  dosage_pattern: string;
  food_timing: string;
  start_date: string;
  end_date: string | null;
  duration_days: number | null;
  reminder_times: ReminderTimesInput | null;
  notes: string | null;
}

export interface ScheduleCompleteRequest {
  reminder_id: number;
}

export interface ScheduleReminderResponse {
  id: number;
  reminder_date: string; // ISO date
  reminder_time: string; // HH:MM:SS
  period: string; // "morning" | "afternoon" | "night"
  completed_at: string | null; // ISO datetime
}

export interface ScheduleResponse {
  id: number;
  medicine_id: number;
  medicine_name: string;
  dosage_pattern: string;
  food_timing: string;
  start_date: string;
  end_date: string;
  duration_days: number | null;
  quantity: number | null;
  quantity_unit: string | null;
  purchase_date: string | null;
  expiry_date: string | null;
  pharmacy_name: string | null;
  notes: string | null;
  status: string; // "active" | "paused" | "completed" | "cancelled"
  source: string; // "manual" | "pharmacy_bill" | "generic_finder"
  reminder_time: string | null; // HH:MM:SS
  reminders: ScheduleReminderResponse[];
}

export interface ScheduleListResponse {
  items: ScheduleResponse[];
}

export interface ScheduleDeleteResponse {
  message: string;
}

// Medical Records types
export type MedicalRecordDocumentType =
  | "prescription"
  | "lab_result"
  | "imaging"
  | "doctor_note"
  | "discharge_summary"
  | "vaccination_record"
  | "insurance"
  | "other";

export interface MedicalRecordDocumentCreate {
  document_type: MedicalRecordDocumentType;
  file_name: string;
  file_type: string;
  file_size: number;
  storage_path: string;
  upload_date: string | null; // ISO datetime string
  doctor_name: string | null;
  hospital_or_clinic: string | null;
  doctor_specialty: string | null;
  consultation_date: string | null; // ISO date string
  follow_up_date: string | null; // ISO date string
  diagnosis: string | null;
  notes: string | null;
    ocr_confidence?: number | null;
    ocr_processed_at?: string | null;
    ocr_source?: string;
    blur_score?: number | null;
    brightness?: number | null;
    contrast?: number | null;
    is_pass?: boolean | null;
    issues?: string[];
}

export interface MedicalRecordCreateRequest {
  title: string;
  folder_name: string;
  description: string | null;
  hospital_name: string | null;
  doctor_name: string | null;
  visit_date: string | null; // ISO date string
  diagnosis: string | null;
  treatment_name: string | null;
  notes: string | null;
  documents: MedicalRecordDocumentCreate[];
  linked_schedule_ids: number[];
  linked_inventory_item_ids: number[];
  linked_medicine_ids: number[];
  linked_generic_search_ids: string[];
}

export interface MedicalRecordUpdateRequest {
  title: string | null;
  folder_name: string | null;
  description: string | null;
  hospital_name: string | null;
  doctor_name: string | null;
  visit_date: string | null; // ISO date string
  diagnosis: string | null;
  treatment_name: string | null;
  notes: string | null;
  documents: MedicalRecordDocumentCreate[] | null;
  linked_generic_search_ids: string[] | null;
}

export interface MedicalRecordLinkRequest {
  record_id: number;
  schedule_ids: number[];
  inventory_item_ids: number[];
  medicine_ids: number[];
}

export interface MedicalRecordDocumentResponse {
  id: number;
  document_type: MedicalRecordDocumentType;
  file_name: string;
  file_type: string;
  file_size: number;
  storage_path: string;
  upload_date: string; // ISO datetime string
  doctor_name: string | null;
  hospital_or_clinic: string | null;
  doctor_specialty: string | null;
  consultation_date: string | null; // ISO date string
  follow_up_date: string | null; // ISO date string
  diagnosis: string | null;
  notes: string | null;
}

export interface MedicalRecordResponse {
  id: number;
  title: string;
  folder_name: string;
  description: string | null;
  hospital_name: string | null;
  doctor_name: string | null;
  visit_date: string | null; // ISO date string
  diagnosis: string | null;
  treatment_name: string | null;
  notes: string | null;
  documents: MedicalRecordDocumentResponse[];
  linked_schedule_ids: number[];
  linked_inventory_item_ids: number[];
  linked_medicine_ids: number[];
  linked_generic_search_ids: string[];
  created_at: string; // ISO datetime string
  updated_at: string; // ISO datetime string
}

export interface MedicalRecordListResponse {
  items: MedicalRecordResponse[];
}

export interface MedicalRecordDeleteResponse {
  message: string;
}

export interface SubmissionResultItem {
  id: string;
  medicineName: string;
  medicineId: number | null;
  status: "added" | "skipped" | "failed";
  error: string | null;
  inventoryItemId?: number;
}

export interface MedicineForInventory {
  id: string;
  medicineId: number | null;
  name: string;
  genericName: string | null;
  brandName: string | null;
  type: MedicineType;
  strength: string | null;
  dosageUnit: string | null;
  quantity: number | null;
  quantityUnit: string | null;
  expiryDate: string | null;
  isSelected: boolean;
  isKnown: boolean;
  isDuplicate: boolean;
  existingInventoryItem: any | null;
  submissionStatus: string;
  error: string | null;
  editField?: string;
  editValue?: string;
  randomId: string;
}