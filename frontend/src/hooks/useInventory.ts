import { useState, useEffect } from "react";
import { inventoryService } from "@/services/inventory.service";
import { useToast } from "@/components/ui/ToastProvider";
import type {
  InventoryResponseItem,
  InventorySummaryResponse,
  InventoryCreateRequest,
  InventoryUpdateRequest,
} from "@/types/api";

export function useInventory() {
  const [inventory, setInventory] = useState<InventoryResponseItem[]>([]);
  const [summary, setSummary] = useState<InventorySummaryResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const { addToast } = useToast();

  const setLoadingState = (isLoading: boolean) => {
    setLoading(isLoading);
  };

  const setErrorState = (err: string | null) => {
    setError(err);
  };

  const setSuccessState = (msg: string | null) => {
    setSuccess(msg);
  };

  const fetchInventory = async () => {
    setLoadingState(true);
    setErrorState(null);
    try {
      const response = await inventoryService.getAll();
      setInventory(response.items);
    } catch (err: any) {
      const message =
        err.response?.data?.message ||
        err.message ||
        "Failed to fetch inventory";
      setErrorState(message);
      setInventory([]);
    } finally {
      setLoadingState(false);
    }
  };

  const fetchSummary = async () => {
    setLoadingState(true);
    setErrorState(null);
    try {
      const response = await inventoryService.getSummary();
      setSummary(response);
    } catch (err: any) {
      const message =
        err.response?.data?.message ||
        err.message ||
        "Failed to fetch inventory summary";
      setErrorState(message);
      setSummary(null);
    } finally {
      setLoadingState(false);
    }
  };

  const refresh = async () => {
    await Promise.all([fetchInventory(), fetchSummary()]);
  };

  const createMedicine = async (data: InventoryCreateRequest) => {
    setLoadingState(true);
    setErrorState(null);
    setSuccessState(null);
    try {
      const response = await inventoryService.create(data);
      setInventory((prev) => [...prev, response]);
      setSuccessState("Medicine added.");
      addToast({
        title: "Medicine added.",
        description: "The medicine has been added to your inventory.",
        variant: "success",
      });
    } catch (err: any) {
      const message =
        err.response?.data?.message ||
        err.message ||
        "Failed to add medicine";
      setErrorState(message);
      addToast({
        title: "Error",
        description: message,
        variant: "destructive",
      });
    } finally {
      setLoadingState(false);
    }
  };

  const updateMedicine = async (
    id: number,
    data: InventoryUpdateRequest
  ) => {
    setLoadingState(true);
    setErrorState(null);
    setSuccessState(null);
    try {
      await inventoryService.update(id, data);
      setInventory((prev) =>
        prev.map((item) => {
          if (item.id === id) {
            const updatedItem: InventoryResponseItem = { ...item };
            if (data.name !== null && data.name !== undefined) {
              updatedItem.name = data.name;
            }
            if (
              data.generic_name !== null &&
              data.generic_name !== undefined
            ) {
              updatedItem.generic_name = data.generic_name;
            }
            if (
              data.brand_name !== null &&
              data.brand_name !== undefined
            ) {
              updatedItem.brand_name = data.brand_name;
            }
            if (
              data.type !== null && data.type !== undefined
            ) {
              updatedItem.type = data.type;
            }
            if (
              data.quantity !== null &&
              data.quantity !== undefined
            ) {
              updatedItem.quantity = data.quantity;
            }
            if (
              data.quantity_unit !== null &&
              data.quantity_unit !== undefined
            ) {
              updatedItem.quantity_unit = data.quantity_unit;
            }
            if (
              data.expiry_date !== null &&
              data.expiry_date !== undefined
            ) {
              updatedItem.expiry_date = data.expiry_date;
            }
            if (
              data.purchase_date !== null &&
              data.purchase_date !== undefined
            ) {
              updatedItem.purchase_date = data.purchase_date;
            }
            if (
              data.image_path !== null &&
              data.image_path !== undefined
            ) {
              updatedItem.image_path = data.image_path;
            }
            if (
              data.notes !== null &&
              data.notes !== undefined
            ) {
              updatedItem.notes = data.notes;
            }
            return updatedItem;
          }
          return item;
        })
      );
      setSuccessState("Medicine updated.");
      addToast({
        title: "Medicine updated.",
        description: "The medicine has been updated in your inventory.",
        variant: "success",
      });
    } catch (err: any) {
      const message =
        err.response?.data?.message ||
        err.message ||
        "Failed to update medicine";
      setErrorState(message);
      addToast({
        title: "Error",
        description: message,
        variant: "destructive",
      });
    } finally {
      setLoadingState(false);
    }
  };

  const deleteMedicine = async (id: number) => {
    setLoadingState(true);
    setErrorState(null);
    setSuccessState(null);
    try {
      await inventoryService.delete(id);
      setInventory((prev) => prev.filter((item) => item.id !== id));
      setSuccessState("Medicine removed.");
      addToast({
        title: "Medicine removed.",
        description: "The medicine has been removed from your inventory.",
        variant: "success",
      });
    } catch (err: any) {
      const message =
        err.response?.data?.message ||
        err.message ||
        "Failed to delete medicine";
      setErrorState(message);
      addToast({
        title: "Error",
        description: message,
        variant: "destructive",
      });
    } finally {
      setLoadingState(false);
    }
  };

  // Fetch on mount
  useEffect(() => {
    fetchInventory();
    fetchSummary();
  }, []);

  return {
    inventory,
    summary,
    loading,
    error,
    success,
    fetchInventory,
    fetchSummary,
    refresh,
    createMedicine,
    updateMedicine,
    deleteMedicine,
  };
}