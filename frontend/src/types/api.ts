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
  recall: any; // can keep type any to avoid breaking; not used in frontend
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
  dosage_form: string; // MedicineType enum as string
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
