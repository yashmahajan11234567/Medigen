/** Shared types consumed across the entire frontend. */

/** Standard single-item API response envelope. */
export interface ApiResponse<T> {
  data: T;
  message?: string;
}

/** Standard paginated list response envelope. */
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

/** Represents every possible loading state a page or section can be in. */
export type LoadingState = "idle" | "loading" | "error" | "success";

/** Generic async state container for any resource. */
export interface AsyncState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  status: LoadingState;
}

/** Normalised API error shape. */
export interface NormalisedApiError {
  message: string;
  status: number | null;
  code: string | null;
  details: Array<Record<string, unknown>> | null;
}