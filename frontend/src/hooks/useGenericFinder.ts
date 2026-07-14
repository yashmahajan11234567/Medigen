import { useState, useEffect } from "react";
import { apiClient } from "@/lib/api-client";
import { useDebounce } from "@/hooks/useDebounce";
import type {
  GenericFinderSearchResponse,
  GenericMedicineSummary,
  AddToInventoryResponse,
} from "@/types/api";

export function useGenericFinder() {
  const [searchTerm, setSearchTerm] = useState("");
  const debouncedSearchTerm = useDebounce(searchTerm, 300);
  const [searchResults, setSearchResults] = useState<GenericFinderSearchResponse | null>(null);
  const [selectedMedicine, setSelectedMedicine] = useState<GenericMedicineSummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Search when debounced search term changes (and is not empty)
  useEffect(() => {
    if (db.trim() === "") {
      setSearchResults(null);
      return;
    }

    const searchMedicines = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await apiClient.get<GenericFinderSearchResponse>(
          "/api/v1/generic/search",
          { params: { brand_name: debouncedSearchTerm } }
        );
        setSearchResults(response.data);
      } catch (err: any) {
        setError(
          err.response?.data?.message ||
            err.message ||
            "An error occurred while searching"
        );
        setSearchResults(null);
        console.error("Search error:", err);
      } finally {
        setLoading(false);
      }
    };

    void searchMedicines();
  }, [debouncedSearchTerm]);

  const selectMedicine = (medicine: GenericMedicineSummary) => {
    setSelectedMedicine(medicine);
  };

  const addToInventory = async () => {
    if (!selectedMedicine) return;
    setLoading(true);
    setError(null);
    setSuccess(null);
    try {
      await apiClient.post<AddToInventoryResponse>(
        "/api/v1/generic/add-to-inventory",
        {
          medicine_id: selectedMedicine.id,
          quantity: null,
          quantity_unit: null,
          expiry_date: null,
        }
      );
      setSuccess("Medicine added to inventory successfully!");
      // Optionally clear selection after success
      setSelectedMedicine(null);
    } catch (err: any) {
      setError(
        err.response?.data?.message ||
          err.message ||
          "Failed to add medicine to inventory"
      );
      console.error("Add to inventory error:", err);
    } finally {
      setLoading(false);
    }
  };

  return {
    searchTerm,
    setSearchTerm,
    searchResults,
    selectedMedicine,
    loading,
    error,
    success,
    selectMedicine,
    addToInventory,
  };
}
