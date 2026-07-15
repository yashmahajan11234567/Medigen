import { useState, useEffect } from "react";
import { apiClient } from "@/lib/api-client";
import type {
  InventoryResponseItem,
  InventoryListResponse,
  InventoryCreateRequest,
  InventoryUpdateRequest,
  InventoryDeleteResponse,
} from "@/types/api";

export function useInventory() {
  const [inventory, setInventory] = useState<InventoryResponseItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const fetchInventory = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiClient.get<InventoryListResponse>("/api/v1/inventory");
      setInventory(response.data.items);
    } catch (err: any) {
      setError(
        err.response?.data?.message || err.message || "Failed to fetch inventory"
      );
      setInventory([]);
    } finally {
      setLoading(false);
    }
  };

  const createInventory = async (data: InventoryCreateRequest) => {
    setLoading(true);
    setError(null);
    setSuccess(null);
    try {
      const response = await apiClient.post<InventoryResponseItem>(
        "/api/v1/inventory",
        data
      );
      setInventory((prev) => [...prev, response.data]);
      setSuccess("Item added to inventory");
    } catch (err: any) {
      setError(
        err.response?.data?.message ||
          err.message ||
          "Failed to add inventory item"
      );
    } finally {
      setLoading(false);
    }
  };

  const updateInventory = async (
    id: number,
    data: InventoryUpdateRequest
  ) => {
    setLoading(true);
    setError(null);
    setSuccess(null);
    try {
      await apiClient.put(`/api/v1/inventory/${id}`, data);
      setInventory((prev) =>
        prev.map((item) => {
          if (item.id === id) {
            // Only update fields that are not null in the data object
            const updatedItem: InventoryResponseItem = { ...item };
            if (data.name !== null && data.name !== undefined) {
              updatedItem.name = data.name;
            }
            if (data.generic_name !== null && data.generic_name !== undefined) {
              updatedItem.generic_name = data.generic_name;
            }
            if (data.brand_name !== null && data.brand_name !== undefined) {
              updatedItem.brand_name = data.brand_name;
            }
            if (data.type !== null && data.type !== undefined) {
              updatedItem.type = data.type;
            }
            if (data.quantity !== null && data.quantity !== undefined) {
              updatedItem.quantity = data.quantity;
            }
            if (data.quantity_unit !== null && data.quantity_unit !== undefined) {
              updatedItem.quantity_unit = data.quantity_unit;
            }
            if (data.expiry_date !== null && data.expiry_date !== undefined) {
              updatedItem.expiry_date = data.expiry_date;
            }
            if (data.purchase_date !== null && data.purchase_date !== undefined) {
              updatedItem.purchase_date = data.purchase_date;
            }
            if (data.image_path !== null && data.image_path !== undefined) {
              updatedItem.image_path = data.image_path;
            }
            if (data.notes !== null && data.notes !== undefined) {
              updatedItem.notes = data.notes;
            }
            return updatedItem;
          }
          return item;
        })
      );
      setSuccess("Inventory item updated");
    } catch (err: any) {
      setError(
        err.response?.data?.message ||
          err.message ||
          "Failed to update inventory item"
      );
    } finally {
      setLoading(false);
    }
  };

  const deleteInventory = async (id: number) => {
    setLoading(true);
    setError(null);
    setSuccess(null);
    try {
      await apiClient.delete<InventoryDeleteResponse>(`/api/v1/inventory/${id}`);
      setInventory((prev) => prev.filter((item) => item.id !== id));
      setSuccess("Inventory item deleted");
    } catch (err: any) {
      setError(
        err.response?.data?.message ||
          err.message ||
          "Failed to delete inventory item"
      );
    } finally {
      setLoading(false);
    }
  };

  // Fetch on mount
  useEffect(() => {
    fetchInventory();
  }, []);

  return {
    inventory,
    loading,
    error,
    success,
    fetchInventory,
    createInventory,
    updateInventory,
    deleteInventory,
  };
}