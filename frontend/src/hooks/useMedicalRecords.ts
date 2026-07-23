import { useState, useCallback } from "react";
import { apiClient } from "@/lib/api-client";
import type {
  MedicalRecordCreateRequest,
  MedicalRecordResponse,
  MedicalRecordListResponse,
  MedicalRecordUpdateRequest,
  MedicalRecordDeleteResponse,
  MedicalRecordLinkRequest,
} from "@/types/api";

export function useMedicalRecords() {
  const [records, setRecords] = useState<MedicalRecordResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const fetchRecords = useCallback(async () => {
    setLoading(true);
    setError(null);
    setSuccess(null);
    try {
      const response = await apiClient.get<MedicalRecordListResponse>("/medical-records");
      setRecords(response.data.items);
    } catch (err: any) {
      const message =
        err.response?.data?.message ||
        err.message ||
        "Failed to fetch medical records";
      setError(message);
      setRecords([]);
    } finally {
      setLoading(false);
    }
  }, []);

  const searchRecords = useCallback(
    async (query: string) => {
      setLoading(true);
      setError(null);
      setSuccess(null);
      try {
        const response = await apiClient.get<MedicalRecordListResponse>(
          "/medical-records/search",
          {
            params: { query },
          }
        );
        setRecords(response.data.items);
      } catch (err: any) {
        const message =
          err.response?.data?.message ||
          err.message ||
          "Failed to search medical records";
        setError(message);
        setRecords([]);
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const filterRecords = useCallback(
    async ({
      documentType,
      hospital,
      dateFrom,
      dateTo,
    }: {
      documentType?: string;
      hospital?: string | undefined;
      dateFrom?: string | null | undefined;
      dateTo?: string | null | undefined;
    }) => {
      setLoading(true);
      setError(null);
      setSuccess(null);
      try {
        const response = await apiClient.get<MedicalRecordListResponse>(
          "/medical-records/filter",
          {
            params: {
              document_type: documentType === "" ? undefined : documentType,
              hospital: hospital === "" ? undefined : hospital,
              date_from: dateFrom === "" ? null : dateFrom,
              date_to: dateTo === "" ? null : dateTo,
            },
          }
        );
        setRecords(response.data.items);
      } catch (err: any) {
        const message =
          err.response?.data?.message ||
          err.message ||
          "Failed to filter medical records";
        setError(message);
        setRecords([]);
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const createRecord = useCallback(
    async (data: MedicalRecordCreateRequest) => {
      setLoading(true);
      setError(null);
      setSuccess(null);
      try {
        const response = await apiClient.post<MedicalRecordResponse>(
          "/medical-records",
          data
        );
        setRecords((prev) => [...prev, response.data]);
        setSuccess("Record created successfully");
        return response.data;
      } catch (err: any) {
        const message =
          err.response?.data?.message ||
          err.message ||
          "Failed to create medical record";
        setError(message);
        throw new Error(message);
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const updateRecord = useCallback(
    async (id: number, data: MedicalRecordUpdateRequest) => {
      setLoading(true);
      setError(null);
      setSuccess(null);
      try {
        await apiClient.put(`/medical-records/${id}`, data);
        setRecords((prev) =>
          prev.map((record) =>
            record.id === id
              ? { ...record, ...(data as Partial<MedicalRecordResponse>) }
              : record
          )
        );
        setSuccess("Record updated successfully");
      } catch (err: any) {
        const message =
          err.response?.data?.message ||
          err.message ||
          "Failed to update medical record";
        setError(message);
        throw new Error(message);
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const deleteRecord = useCallback(
    async (id: number) => {
      setLoading(true);
      setError(null);
      setSuccess(null);
      try {
        const response = await apiClient.delete<MedicalRecordDeleteResponse>(
          `/medical-records/${id}`
        );
        setRecords((prev) => prev.filter((record) => record.id !== id));
        setSuccess("Record deleted successfully");
        return response.data;
      } catch (err: any) {
        const message =
          err.response?.data?.message ||
          err.message ||
          "Failed to delete medical record";
        setError(message);
        throw new Error(message);
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const linkRecord = useCallback(
    async (payload: MedicalRecordLinkRequest) => {
      setLoading(true);
      setError(null);
      setSuccess(null);
      try {
        const response = await apiClient.post<MedicalRecordResponse>(
          "/medical-records/link",
          payload
        );
        // Update the record in the list if it exists
        setRecords((prev) =>
          prev.map((record) =>
            record.id === payload.record_id
              ? { ...record, ...response.data }
              : record
          )
        );
        setSuccess("Record linked successfully");
        return response.data;
      } catch (err: any) {
        const message =
          err.response?.data?.message ||
          err.message ||
          "Failed to link medical record";
        setError(message);
        throw new Error(message);
      } finally {
        setLoading(false);
      }
    },
    []
  );

  return {
    records,
    loading,
    error,
    success,
    fetchRecords,
    searchRecords,
    filterRecords,
    createRecord,
    updateRecord,
    deleteRecord,
    linkRecord,
  };
}