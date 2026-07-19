import { apiClient } from "@/lib/api-client";
import type {
  GenericFinderSearchResponse,
  AddToInventoryRequest,
  AddToInventoryResponse,
} from "@/types/api";

export const genericFinderService = {
  search(medicineName: string): Promise<GenericFinderSearchResponse> {
    return apiClient
      .post<GenericFinderSearchResponse>("/generic-finder/search", { medicine_name: medicineName })
      .then((r) => r.data);
  },

  addToInventory(payload: AddToInventoryRequest): Promise<AddToInventoryResponse> {
    return apiClient
      .post<AddToInventoryResponse>("/generic-finder/add-to-inventory", payload)
      .then((r) => r.data);
  },
};