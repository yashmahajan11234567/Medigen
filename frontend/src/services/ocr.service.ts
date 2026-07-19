import { apiClient } from "@/lib/api-client";
import type { GenericMedicineSummary } from "@/types/api";

/**
 * Represents a medicine extracted from an OCR scan.
 * Extends the existing GenericMedicineSummary to reuse known fields.
 */
export interface OcrExtractedMedicine extends GenericMedicineSummary {
  // Additional OCR‑specific fields could be added here if needed
  confidence?: number;
}

/**
 * Uploads an image file to the OCR backend and returns the extracted medicines.
 * The backend is expected to accept multipart/form-data at /api/v1/ocr/process
 * and respond with an array of extracted medicine details.
 */
export const ocrService = {
  async processImage(formData: FormData): Promise<OcrExtractedMedicine[]> {
    try {
      const response = await apiClient.post<any>(
        "/api/v1/ocr/process",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );
      // Assume the backend returns an array of extracted medicine objects
      return response.data as OcrExtractedMedicine[];
    } catch (err: any) {
      // Re‑throw for centralized error handling in components
      throw err;
    }
  },
};