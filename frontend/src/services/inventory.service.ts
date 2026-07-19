import { apiClient } from "@/lib/api-client";
import type {
  InventoryCreateRequest,
  InventoryListResponse,
  InventoryResponseItem,
  InventorySummaryResponse,
  InventoryUpdateRequest,
  InventoryDeleteResponse,
} from "@/types/api";

export const inventoryService = {
  getAll(): Promise<InventoryListResponse> {
    return apiClient.get<InventoryListResponse>("/inventory").then((r) => r.data);
  },

  getSummary(): Promise<InventorySummaryResponse> {
    return apiClient.get<InventorySummaryResponse>("/inventory/summary").then((r) => r.data);
  },

  getById(id: number): Promise<InventoryResponseItem> {
    return apiClient.get<InventoryResponseItem>(`/inventory/${id}`).then((r) => r.data);
  },

  create(payload: InventoryCreateRequest): Promise<InventoryResponseItem> {
    return apiClient.post<InventoryResponseItem>("/inventory", payload).then((r) => r.data);
  },

  update(id: number, payload: InventoryUpdateRequest): Promise<InventoryResponseItem> {
    return apiClient.put<InventoryResponseItem>(`/inventory/${id}`, payload).then((r) => r.data);
  },

  delete(id: number): Promise<InventoryDeleteResponse> {
    return apiClient.delete<InventoryDeleteResponse>(`/inventory/${id}`).then((r) => r.data);
  },
};