import { apiClient } from "@/lib/api-client";
import type {
  MedicalRecordCreateRequest,
  MedicalRecordDeleteResponse,
  MedicalRecordListResponse,
  MedicalRecordResponse,
  MedicalRecordUpdateRequest,
} from "@/types/api";

export const medicalRecordsService = {
  getAll(): Promise<MedicalRecordListResponse> {
    return apiClient.get<MedicalRecordListResponse>("/medical-records").then((r) => r.data);
  },

  search(query: string): Promise<MedicalRecordListResponse> {
    return apiClient
      .get<MedicalRecordListResponse>("/medical-records/search", { params: { query } })
      .then((r) => r.data);
  },

  filter(params: {
    documentType?: string;
    hospital?: string;
    dateFrom?: string;
    dateTo?: string;
  }): Promise<MedicalRecordListResponse> {
    return apiClient
      .get<MedicalRecordListResponse>("/medical-records/filter", { params })
      .then((r) => r.data);
  },

  getById(id: number): Promise<MedicalRecordResponse> {
    return apiClient.get<MedicalRecordResponse>(`/medical-records/${id}`).then((r) => r.data);
  },

  create(payload: MedicalRecordCreateRequest): Promise<MedicalRecordResponse> {
    return apiClient.post<MedicalRecordResponse>("/medical-records", payload).then((r) => r.data);
  },

  update(id: number, payload: MedicalRecordUpdateRequest): Promise<MedicalRecordResponse> {
    return apiClient
      .put<MedicalRecordResponse>(`/medical-records/${id}`, payload)
      .then((r) => r.data);
  },

  delete(id: number): Promise<MedicalRecordDeleteResponse> {
    return apiClient
      .delete<MedicalRecordDeleteResponse>(`/medical-records/${id}`)
      .then((r) => r.data);
  },
};