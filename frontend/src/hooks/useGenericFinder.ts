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
  const [results, setResults] = useState<GenericMedicineSummary[]>([]);
  const [selectedMedicine, setSelectedMedicine] = useState<GenericMedicineSummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);\n  const [apiMessage, setApiMessage] = useState<string | null>(null);

  // Search when debounced search term changes (and is not empty)
  useEffect(() => {
    if (debouncedSearchTerm.trim() === "") {
      setResults([]);
      return;
    }\n      setApiMessage(null);

    const searchMedicines = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await apiClient.post<GenericFinderSearchResponse>(
          "/api/v1/generic/search",
          { medicine_name: debouncedSearchTerm }
        );
        setResults(response.data.matches);\n        setApiMessage(response.data.message);
      } catch (err: any) {
        setError(
          err.response?.data?.message ||
            err.message ||
            "An error occurred while searching"
        );
        setResults([]);
        console.error("Search error:", err);\n      setApiMessage(null);
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

  return {\n    searchTerm,\n    setSearchTerm,\n    results,\n    selectedMedicine,\n    loading,\n    error,\n    success,\n    selectMedicine,\n    addToInventory,\n    apiMessage,\n  };;\n    apiMessage,\n  };
}







