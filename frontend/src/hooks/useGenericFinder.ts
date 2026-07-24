import { useState, useEffect, useRef, useCallback } from "react";
import { genericFinderService } from "@/services/genericFinder.service";
import { useDebounce } from "@/hooks/useDebounce";
import type {
  GenericFinderSearchResponse,
  GenericMedicineSummary,
  AddToInventoryResponse,
} from "@/types/api";

const MIN_SEARCH_LENGTH = 2;

export function useGenericFinder() {
  const [searchTerm, setSearchTerm] = useState("");
  const debouncedSearchTerm = useDebounce(searchTerm, 300);
  const [results, setResults] = useState<GenericMedicineSummary[]>([]);
  const [selectedMedicine, setSelectedMedicine] = useState<GenericMedicineSummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [apiMessage, setApiMessage] = useState<string | null>(null);

  // Request ID pattern for stale response prevention
  const requestIdRef = useRef(0);
  // AbortController for cleanup on unmount
  const abortControllerRef = useRef<AbortController | null>(null);

  // Search when debounced search term changes (and is not empty)
  useEffect(() => {
    const trimmedTerm = debouncedSearchTerm.trim();

    // FIX 2: Minimum length guard - clear results and don't call API
    if (trimmedTerm.length < MIN_SEARCH_LENGTH) {
      setResults([]);
      setError(null);
      setApiMessage(null);
      setLoading(false);
      return;
    }

    // Increment request ID for stale response prevention
    const currentRequestId = ++requestIdRef.current;

    // Create new AbortController for this request
    const controller = new AbortController();
    abortControllerRef.current = controller;

    setApiMessage(null);

    const searchMedicines = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await genericFinderService.search(trimmedTerm);

        // FIX 3: Ignore stale responses
        if (currentRequestId !== requestIdRef.current) {
          return;
        }

        setResults(response.matches);
        setApiMessage(response.message);
      } catch (err: any) {
        // FIX 3: Ignore errors from stale requests
        if (currentRequestId !== requestIdRef.current) {
          return;
        }
        // Ignore abort errors
        if (err.name === "AbortError" || err.code === "ECONNABORTED") {
          return;
        }
        setError(
          err.response?.data?.message ||
            err.message ||
            "An error occurred while searching"
        );
        setResults([]);
        console.error("Search error:", err);
        setApiMessage(null);
      } finally {
        // FIX 3: Only update loading if this is still the current request
        if (currentRequestId === requestIdRef.current) {
          setLoading(false);
        }
      }
    };

    void searchMedicines();

    // FIX 4: Cleanup on unmount or when effect re-runs
    return () => {
      controller.abort();
    };
  }, [debouncedSearchTerm]);

  const selectMedicine = useCallback((medicine: GenericMedicineSummary) => {
    setSelectedMedicine(medicine);
  }, []);

  const addToInventory = useCallback(async () => {
    if (!selectedMedicine) return;
    setLoading(true);
    setError(null);
    setSuccess(null);
    try {
      await genericFinderService.addToInventory({
        medicine_id: selectedMedicine.id,
        quantity: null,
        quantity_unit: null,
        expiry_date: null,
      });
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
  }, [selectedMedicine]);

  return {
    searchTerm,
    setSearchTerm,
    results,
    selectedMedicine,
    loading,
    error,
    success,
    selectMedicine,
    addToInventory,
    apiMessage,
  };
}
