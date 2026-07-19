import { useState } from "react";
import { Camera, Keyboard, X, Check, Loader2 } from "lucide-react";
import { cn } from "@/lib/cn";
import { useToast } from "@/components/ui/ToastProvider";
import type { InventoryCreateRequest } from "@/types/api";

interface AddMedicineModalProps {
  open: boolean;
  onClose: () => void;
  onAdd: (data: InventoryCreateRequest) => Promise<void>;
}

export function AddMedicineModal({ open, onClose, onAdd }: AddMedicineModalProps) {
  const [tab, setTab] = useState<'scan' | 'manual'>('scan');
  const [formData, setFormData] = useState<Partial<InventoryCreateRequest>>({
    medicine_id: null,
    name: null,
    generic_name: null,
    brand_name: null,
    type: "tablet" as const,
    quantity: null,
    quantity_unit: null,
    expiry_date: null,
    purchase_date: null,
    image_path: null,
    notes: null,
  });
  const [loading, setLoading] = useState(false);
  const { addToast } = useToast();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      // Ensure all fields are present and convert empty strings to null
      const payload: InventoryCreateRequest = {
        medicine_id: formData.medicine_id ?? null,
        name: formData.name ?? null,
        generic_name: formData.generic_name ?? null,
        brand_name: formData.brand_name ?? null,
        type: formData.type ?? "tablet",
        quantity: formData.quantity ?? null,
        quantity_unit: formData.quantity_unit ?? null,
        expiry_date: formData.expiry_date ?? null,
        purchase_date: formData.purchase_date ?? null,
        image_path: formData.image_path ?? null,
        notes: formData.notes ?? null,
      };
      await onAdd(payload as InventoryCreateRequest);
      // Reset form
      setFormData({
        medicine_id: null,
        name: null,
        generic_name: null,
        brand_name: null,
        type: "tablet" as const,
        quantity: null,
        quantity_unit: null,
        expiry_date: null,
        purchase_date: null,
        image_path: null,
        notes: null,
      });
      setTab("scan");
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
      addToast({
        title: "Error",
        description: message,
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  if (!open) return null;

  return (
    <>
      <div className="fixed inset-0 z-50 bg-black/30 backdrop-blur-sm" onClick={onClose} />
      <div className="fixed inset-x-4 top-1/2 z-50 -translate-y-1/2 sm:inset-x-auto sm:left-1/2 sm:w-full sm:max-w-md sm:-translate-x-1/2">
        <div className="rounded-3xl bg-white p-6 shadow-2xl">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-slate-900">Add Medicine</h2>
            <button
              type="button"
              onClick={onClose}
              className="flex h-9 w-9 items-center justify-center rounded-xl bg-slate-100 text-slate-500 transition hover:bg-slate-200"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          <div className="mb-4">
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => setTab("scan")}
                className={cn(
                  "flex-1 items-center justify-between rounded-2xl px-4 py-2 text-sm font-medium transition",
                  tab === "scan"
                    ? "bg-brand-500 text-white"
                    : "bg-slate-50 text-slate-600 hover:bg-slate-100",
                )}
              >
                <Camera className="mr-2 h-4 w-4" />
                Scan Medicine Box
              </button>
              <button
                type="button"
                onClick={() => setTab("manual")}
                className={cn(
                  "flex-1 items-center justify-between rounded-2xl px-4 py-2 text-sm font-medium transition",
                  tab === "manual"
                    ? "bg-brand-500 text-white"
                    : "bg-slate-50 text-slate-600 hover:bg-slate-100",
                )}
              >
                <Keyboard className="mr-2 h-4 w-4" />
                Manual Entry
              </button>
            </div>
          </div>

          {tab === "scan" ? (
            <div className="text-center py-8">
              <div className="mx-auto h-12 w-12 rounded-blade bg-brand-50 text-brand-600 flex items-center justify-center mb-4">
                <Camera className="h-6 w-6" />
              </div>
              <h3 className="font-semibold text-slate-900 mb-2">Scan Medicine Barcode</h3>
              <p className="text-sm text-slate-600 mb-6">
                Point your camera at the medicine barcode to automatically fill in the details.
              </p>
              <button
                type="button"
                onClick={() => {
                  addToast({
                    title: "Not Implemented",
                    description: "The scan feature is not yet implemented.",
                    variant: "destructive",
                  });
                }}
                className="w-full flex items-center justify-center px-4 py-2 rounded-md border border-transparent bg-brand-500 text-white hover:bg-brand-600"
              >
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Scanning...
                  </>
                ) : (
                  "Scan Barcode"
                )}
              </button>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Medicine Name
                </label>
                <input
                  type="text"
                  value={formData.name ?? ""}
                  onChange={(e) =>
                    setFormData((prev) => ({ ...prev, name: e.target.value }))
                  }
                  className="w-full px-4 py-2 rounded-border border-slate-200 focus:ring-2 focus:ring-brand-200"
                  placeholder="Enter medicine name"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Generic Name
                  </label>
                  <input
                    type="text"
                    value={formData.generic_name ?? ""}
                    onChange={(e) =>
                      setFormData((prev) => ({
                        ...prev,
                        generic_name: e.target.value,
                      }))
                    }
                    className="w-full px-4 py-2 rounded-border border-slate-200 focus:ring-2 focus:ring-brand-200"
                    placeholder="Enter generic name (optional)"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Brand Name
                  </label>
                  <input
                    type="text"
                    value={formData.brand_name ?? ""}
                    onChange={(e) =>
                      setFormData((prev) => ({
                        ...prev,
                        brand_name: e.target.value,
                      }))
                    }
                    className="w-full px-4 py-2 rounded-border border-slate-200 focus:ring-2 focus:ring-brand-200"
                    placeholder="Enter brand name (optional)"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Type
                  </label>
                  <select
                    value={formData.type ?? "tablet"}
                    onChange={(e) =>
                      setFormData((prev) => ({
                        ...prev,
                        type: e.target.value as any,
                      }))
                    }
                    className="w-full px-4 py-2 rounded-border border-slate-200 focus:ring-2 focus:ring-brand-200"
                  >
                    <option value="tablet">Tablet</option>
                    <option value="capsule">Capsule</option>
                    <option value="syrup">Syrup</option>
                    <option value="cream">Cream</option>
                    <option value="injection">Injection</option>
                    <option value="ointment">Ointment</option>
                    <option value="drops">Drops</option>
                    <option value="inhaler">Inhaler</option>
                    <option value="other">Other</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Quantity
                    <span className="ml-2 text-xs text-slate-400">(optional)</span>
                  </label>
                  <input
                    type="number"
                    value={formData.quantity ?? ""}
                    onChange={(e) =>
                      setFormData((prev) => ({
                        ...prev,
                        quantity: e.target.value === "" ? null : Number(e.target.value),
                      }))
                    }
                    className="w-full px-4 py-2 rounded-border border-slate-200 focus:ring-2 focus:ring-brand-200"
                    min="0"
                    placeholder="Enter quantity"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Quantity Unit
                    <span className="ml-2 text-xs text-slate-400">(optional)</span>
                  </label>
                  <input
                    type="text"
                    value={formData.quantity_unit ?? ""}
                    onChange={(e) =>
                      setFormData((prev) => ({
                        ...prev,
                        quantity_unit: e.target.value,
                      }))
                    }
                    className="w-full px-4 py-2 rounded-border border-slate-200 focus:ring-2 focus:ring-brand-200"
                    placeholder="e.g., tablets, ml, etc."
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Expiry Date
                    <span className="ml-2 text-xs text-slate-400">(optional)</span>
                  </label>
                  <input
                    type="date"
                    value={formData.expiry_date ?? ""}
                    onChange={(e) =>
                      setFormData((prev) => ({
                        ...prev,
                        expiry_date: e.target.value,
                      }))
                    }
                    className="w-full px-4 py-2 rounded-border border-slate-200 focus:ring-2 focus:ring-brand-200"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Purchase Date
                    <span className="ml-2 text-xs text-slate-400">(optional)</span>
                  </label>
                  <input
                    type="date"
                    value={formData.purchase_date ?? ""}
                    onChange={(e) =>
                      setFormData((prev) => ({
                        ...prev,
                        purchase_date: e.target.value,
                      }))
                    }
                    className="w-full px-4 py-2 rounded-border border-slate-200 focus:ring-2 focus:ring-brand-200"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Image Path
                    <span className="ml-2 text-xs text-slate-400">(optional)</span>
                  </label>
                  <input
                    type="text"
                    value={formData.image_path ?? ""}
                    onChange={(e) =>
                      setFormData((prev) => ({
                        ...prev,
                        image_path: e.target.value,
                      }))
                    }
                    className="w-full px-4 py-2 rounded-border border-slate-200 focus:ring-2 focus:ring-brand-200"
                    placeholder="URL or path to image (optional)"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Notes
                  <span className="ml-2 text-xs text-slate-400">(optional)</span>
                </label>
                <textarea
                  value={formData.notes ?? ""}
                  onChange={(e) =>
                    setFormData((prev) => ({
                      ...prev,
                      notes: e.target.value,
                    }))
                  }
                  className="w-full px-4 py-2 rounded-border border-slate-200 focus:ring-2 focus:ring-brand-200"
                  rows={3}
                  placeholder="Additional notes (optional)"
                />
              </div>

              <div className="pt-4">
                <button
                  type="submit"
                  disabled={loading}
                  className={`
                    w-full flex items-center justify-center px-4 py-2 rounded-md border
                    border-transparent bg-brand-500 text-white hover:bg-brand-600
                    disabled:opacity-50 disabled:cursor-not-allowed
                    transition-colors
                  `}
                >
                  {loading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Adding...
                    </>
                  ) : (
                    <>
                      <Check className="mr-2 h-4 w-4" />
                      Add Medicine
                    </>
                  )}
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </>
  );
}