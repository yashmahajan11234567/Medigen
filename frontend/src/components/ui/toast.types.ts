export type ToastVariant = "default" | "destructive" | "success";

export interface ToastProps {
  id: string;
  title: string;
  description?: string;
  variant: ToastVariant;
  duration?: number;
}