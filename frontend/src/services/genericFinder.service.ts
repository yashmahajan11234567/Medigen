import { apiClient } from "@/lib/api-client";
import type {
  GenericFinderSearchResponse,
  AddToInventoryRequest,
  AddToInventoryResponse,
} from "@/types/api";

export const genericFinderService = {
  search(brandName: string): Promise<GenericFinderSearchResponse> {
    return apiClient
      .get<GenericFinderSearchResponse>("/api/v1/generic/search", {
        params: { brand_name: brandName },
      })
      .then((r) => r.data);
  },

  addToInventory(payload: AddToInventoryRequest): Promise<AddToInventoryResponse> {
    return apiClient
      .post<AddToInventoryResponse>("/api/v1/generic/add-to-inventory", payload)
      .then((r) => r.data);
  },
};
