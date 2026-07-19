import { createContext, useContext, useState, useMemo, ReactNode } from "react";
import type { ToastProps, ToastVariant } from "./toast.types";

export type { ToastProps, ToastVariant } from "./toast.types";

interface ToastContextProps {
  toasts: ToastProps[];
  addToast: (toast: Omit<ToastProps, "id">) => void;
  removeToast: (id: string) => void;
}

const ToastContext = createContext<ToastContextProps | undefined>(undefined);

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<ToastProps[]>([]);

  const addToast = (toast: Omit<ToastProps, "id">) => {
    const id = Math.random().toString(36).substring(2, 9);
    const toastWithId: ToastProps = {
      ...toast,
      id,
      variant: toast.variant ?? "default",
    };
    setToasts((prev) => [...prev, toastWithId]);

    // Auto-remove after duration (default 3000ms)
    const duration = toast.duration ?? 3000;
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, duration);
  };

  const removeToast = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  const value = useMemo(
    () => ({
      toasts,
      addToast,
      removeToast,
    }),
    [toasts]
  );

  return (
    <ToastContext.Provider value={value}>
      {children}
      <ToastContainer toasts={toasts} onRemove={removeToast} />
    </ToastContext.Provider>
  );
}

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error("useToast must be used within a ToastProvider");
  }
  return context;
}

interface ToastContainerProps {
  toasts: ToastProps[];
  onRemove: (id: string) => void;
}

function ToastContainer({ toasts, onRemove }: ToastContainerProps) {
  if (toasts.length === 0) return null;

  return (
    <div className="fixed top-4 right-4 z-50 flex flex-col-reverse space-y-3 sm:max-w-xs">
      {toasts.map((t) => (
        <Toast
          key={t.id}
          {...t}
          onClose={() => onRemove(t.id)}
        />
      ))}
    </div>
  );
}

function Toast({
  title,
  description,
  variant = "default",
  onClose,
}: ToastProps & { onClose: () => void }) {
  const variantConfig: Record<
    ToastVariant,
    { bg: string; text: string; border: string }
  > = {
    default: { bg: "bg-primary", text: "text-primary-foreground", border: "border-primary" },
    destructive: { bg: "bg-destructive", text: "text-destructive-foreground", border: "border-destructive" },
    success: { bg: "bg-success", text: "text-success-foreground", border: "border-success" },
  };

  const { bg, text, border } = variantConfig[variant];

  return (
    <div
      className={`
        flex w-full items-center justify-between space-x-4 rounded-md border p-4
        ${bg} ${text} ${border} shadow-lg
      `}
      role="alert"
    >
      <div className="flex space-x-3 text-sm font-medium">
        <div className="flex-shrink-0 h-3 w-3 rounded-full">
          <div className="h-full w-full" style={{ backgroundColor: getVariantColor(variant) }}></div>
        </div>
        <div className="space-y-1">
          <p className="">{title}</p>
          {description && <p className="text-sm text-muted-foreground">{description}</p>}
        </div>
      </div>
      <div className="flex-shrink-0">
        <button
          onClick={onClose}
          className="ml-2 rounded-half p-1 hover:bg-gray-200"
          aria-label="Dismiss"
        >
          <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>
  );
}

function getVariantColor(variant: ToastVariant): string {
  const colors: Record<ToastVariant, string> = {
    default: "#3b82f6", // blue-500
    destructive: "#ef4444", // red-500
    success: "#10b981", // emerald-500
  };
  return colors[variant];
}