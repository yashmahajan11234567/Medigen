import axios from "axios";
import { AUTH_TOKEN_KEY } from "@/lib/storage";
import { appConfig } from "@/lib/app-config";
import type {
  OCRCompositionResponse,
  OCRPharmacyBillResponse,
  OCRDocumentResponse,
} from "@/types/api";

const OCR_BASE = appConfig.apiBaseUrl.replace("/api/v1", "");

const ocrClient = axios.create({
  baseURL: OCR_BASE,
  timeout: 60000,
});

ocrClient.interceptors.request.use((config) => {
  const token = window.localStorage.getItem(AUTH_TOKEN_KEY);
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  config.headers["Content-Type"] = "multipart/form-data";
  return config;
});

function fileToFormData(file: File): FormData {
  const formData = new FormData();
  formData.append("file", file);
  return formData;
}

export const ocrService = {
  async scanComposition(formData: FormData): Promise<OCRCompositionResponse> {
    const { data } = await ocrClient.post<OCRCompositionResponse>(
      "/ocr/composition",
      formData,
    );
    return data;
  },

  async composition(file: File): Promise<OCRCompositionResponse> {
    return ocrService.scanComposition(fileToFormData(file));
  },

  async scanPharmacyBill(formData: FormData): Promise<OCRPharmacyBillResponse> {
    const { data } = await ocrClient.post<OCRPharmacyBillResponse>(
      "/ocr/pharmacy-bill",
      formData,
    );
    return data;
  },

  async pharmacyBill(file: File): Promise<OCRPharmacyBillResponse> {
    return ocrService.scanPharmacyBill(fileToFormData(file));
  },

  async scanDocument(formData: FormData): Promise<OCRDocumentResponse> {
    const { data } = await ocrClient.post<OCRDocumentResponse>(
      "/ocr/document",
      formData,
    );
    return data;
  },

  async document(file: File): Promise<OCRDocumentResponse> {
    return ocrService.scanDocument(fileToFormData(file));
  },
};