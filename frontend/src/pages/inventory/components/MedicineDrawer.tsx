import { useState, useEffect } from "react";
import { X, Loader2, Check } from "lucide-react";
import { cn } from "@/lib/cn";
import type { MedicineItem } from "@/pages/inventory/components/MedicineGrid";
import type { MedicineType, InventoryUpdateRequest } from "@/types/api";

interface MedicineDrawerProps {
  medicine: MedicineItem | null;
  onClose: () => void;
  onUpdate: (id: number, data: InventoryUpdateRequest) => Promise<void>;
  onDelete: (id: number) => Promise<void>;
}

export function MedicineDrawer({ medicine, onClose, onUpdate, onDelete }: MedicineDrawerProps) {
  // Determine if we are in create mode (medicine is null or has id 0)
  const isCreate = !medicine || (medicine && medicine.id === 0);
  // Use a dummy medicine object for create mode to avoid null checks
  const medicineToUse: MedicineItem = medicine ?? {
    id: 0,
    name: "",
    genericName: "",
    brandName: "",
    type: "tablet",
    quantity: null,
    quantityUnit: null,
    expiryDate: null,
    purchaseDate: null,
    imagePath: null,
    notes: null,
    status: "healthy",
    storageInstructions: "",
  };

  const [editMode, setEditMode] = useState<boolean>(isCreate); // Start in edit mode for create, view mode for existing
  const [editFormData, setEditFormData] = useState<InventoryUpdateRequest>({
    name: null,
    generic_name: null,
    brand_name: null,
    type: null,
    quantity: null,
    quantity_unit: null,
    expiry_date: null,
    purchase_date: null,
    image_path: null,
    notes: null,
  });
  const [loading, setLoading] = useState(false);

  // Initialize form with medicine values when medicine changes or we enter edit mode
  useEffect(() => {
    if (medicineToUse && editMode) {
      setEditFormData({
        name: medicineToUse.name ?? null,
        generic_name: medicineToUse.genericName ?? null,
        brand_name: medicineToUse.brandName ?? null,
        type: medicineToUse.type,
        quantity: medicineToUse.quantity ?? null,
        quantity_unit: medicineToUse.quantityUnit ?? null,
        expiry_date: medicineToUse.expiryDate ?? null,
        purchase_date: medicineToUse.purchaseDate ?? null,
        image_path: medicineToUse.imagePath ?? null,
        notes: medicineToUse.notes ?? null,
      });
    }
  }, [medicineToUse, editMode]);

  const handleSave = async () => {
    setLoading(true);
    try {
      const payload: InventoryUpdateRequest = {
        ...editFormData,
        name: editFormData.name === "" ? null : editFormData.name,
        generic_name: editFormData.generic_name === "" ? null : editFormData.generic_name,
        brand_name: editFormData.brand_name === "" ? null : editFormData.brand_name,
        type: editFormData.type as MedicineType | null,
        quantity: editFormData.quantity,
        quantity_unit: editFormData.quantity_unit === "" ? null : editFormData.quantity_unit,
        expiry_date: editFormData.expiry_date === "" ? null : editFormData.expiry_date,
        purchase_date: editFormData.purchase_date === "" ? null : editFormData.purchase_date,
        image_path: editFormData.image_path === "" ? null : editFormData.image_path,
        notes: editFormData.notes === "" ? null : editFormData.notes,
      };
      await onUpdate(medicineToUse.id, payload);
      setEditMode(false);
    } catch (err: any) {
      // Error is handled by the hook and shown via toast and error state
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    setLoading(true);
    try {
      await onDelete(medicineToUse.id);
      onClose();
    } catch (err: any) {
      // Error handled by hook
    } finally {
      setLoading(false);
    }
  };

  // We never return null now; we always render the drawer (for create or edit)
  const statusConfig = {
    healthy: { label: "Healthy", dot: "bg-mint-500", bg: "bg-mint-50", text: "text-mint-700" },
    low: { label: "Low Stock", dot: "bg-amber-500", bg: "bg-amber-50", text: "text-amber-700" },
    expiring: { label: "Expiring Soon", dot: "bg-amber-500", bg: "bg-amber-50", text: "text-amber-700" },
    expired: { label: "Expired", dot: "bg-rose-500", bg: "bg-rose-50", text: "text-rose-700" },
  };

  const s = statusConfig[
    medicineToUse.status as keyof typeof statusConfig
  ] ?? statusConfig.healthy;

  return (
    <>
      <div
        className="fixed inset-0 z-40 bg-black/30 backdrop-blur-sm lg:bg-black/20"
        onClick={onClose}
      />
      <div
        className={cn(
          "fixed z-50 bg-white shadow-2xl transition-transform",
          "bottom-0 left-0 right-0 max-h-[85vh] rounded-t-3xl lg:bottom-auto lg:left-auto lg:right-0 lg:top-0 lg:h-full lg:w-[420px] lg:rounded-l-3xl lg:rounded-tr-none",
        )}
      >
        <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-brand-100 text-brand-600">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-6 w-6"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth={1.5}
            stroke="currentColor"
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div className="flex items-center justify-between w-full">
          <div>
            {isCreate ? (
              <h2 className="text-xl font-semibold text-slate-900">Add New Medicine</h2>
            ) : (
              <h2 className="text-xl font-semibold text-slate-900">
                {medicineToUse.name}
              </h2>
            )}
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600">
            <X className="h-4 w-4" />
          </button>
        </div>
        {!isCreate && (
          <div>
            <h2 className="text-xl font-semibold text-slate-900">
              {medicineToUse.name}
            </h2>
            <span className={cn("rounded-full px-3 py-0.5 text-xs font-semibold", s.bg, s.text)}>
              {s.label}
            </span>
          </div>
        )}
        <div className="flex-1 overflow-y-auto p-5">
          {editMode ? (
            <form onSubmit={(e) => {
              e.preventDefault();
              handleSave();
            }} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Medicine Name
                </label>
                <input
                  type="text"
                  value={editFormData.name ?? ""}
                  onChange={(e) =>
                    setEditFormData((prev) => ({
                      ...prev,
                      name: e.target.value,
                    }))
                  }
                  className="w-full px-4 py-2 rounded-border border-slate-200 focus:ring-2 focus:ring-brand-200"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Generic Name
                  </label>
                  <input
                    type="text"
                    value={editFormData.generic_name ?? ""}
                    onChange={(e) =>
                      setEditFormData((prev) => ({
                        ...prev,
                        generic_name: e.target.value,
                      }))
                    }
                    className="w-full px-4 py-2 rounded-border border-slate-200 focus:ring-2 focus:ring-brand-200"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Brand Name
                  </label>
                  <input
                    type="text"
                    value={editFormData.brand_name ?? ""}
                    onChange={(e) =>
                      setEditFormData((prev) => ({
                        ...prev,
                        brand_name: e.target.value,
                      }))
                    }
                    className="w-full px-4 py-2 rounded-border border-slate-200 focus:ring-2 focus:ring-brand-200"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Type
                  </label>
                  <select
                    value={editFormData.type ?? "tablet"}
                    onChange={(e) =>
                      setEditFormData((prev) => ({
                        ...prev,
                        type: e.target.value as MedicineType | null,
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
                    value={editFormData.quantity ?? ""}
                    onChange={(e) =>
                      setEditFormData((prev) => ({
                        ...prev,
                        quantity: e.target.value === "" ? null : Number(e.target.value),
                      }))
                    }
                    className="w-full px-4 py-2 rounded-border border-slate-200 focus:ring-2 focus:ring-brand-200"
                    min="0"
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
                    value={editFormData.quantity_unit ?? ""}
                    onChange={(e) =>
                      setEditFormData((prev) => ({
                        ...prev,
                        quantity_unit: e.target.value,
                      }))
                    }
                    className="w-full px-4 py-2 rounded-border border-slate-200 focus:ring-2 focus:ring-brand-200"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Expiry Date
                    <span className="ml-2 text-xs text-slate-400">(optional)</span>
                  </label>
                  <input
                    type="date"
                    value={editFormData.expiry_date ?? ""}
                    onChange={(e) =>
                      setEditFormData((prev) => ({
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
                    value={editFormData.purchase_date ?? ""}
                    onChange={(e) =>
                      setEditFormData((prev) => ({
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
                    value={editFormData.image_path ?? ""}
                    onChange={(e) =>
                      setEditFormData((prev) => ({
                        ...prev,
                        image_path: e.target.value,
                      }))
                    }
                    className="w-full px-4 py-2 rounded-border border-slate-200 focus:ring-2 focus:ring-brand-200"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Notes
                  <span className="ml-2 text-xs text-slate-400">(optional)</span>
                </label>
                <textarea
                  value={editFormData.notes ?? ""}
                  onChange={(e) =>
                    setEditFormData((prev) => ({
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
                      Saving...
                    </>
                  ) : (
                    <>
                      <Check className="mr-2 h-4 w-4" />
                      Save
                    </>
                  )}
                </button>
                <button
                  type="button"
                  onClick={() => setEditMode(false)}
                  className="mt-2 w-full flex items-center justify-center px-4 py-2 rounded-md border border-slate-200 bg-slate-50 text-slate-600 hover:bg-slate-100"
                >
                  Cancel
                </button>
              </div>
            </form>
          ) : (
            <div>
              {!isCreate && (
                <>
                  <div className="mb-5 flex h-32 items-center justify-center rounded-2xl bg-gradient-to-br from-brand-50 to-mint-50">
                    <span className="text-5xl opacity-60">💊</span>
                  </div>

                  <div className="mb-4">
                    <div className="flex items-center gap-2">
                      <h3 className="text-xl font-semibold text-slate-900">
                        {medicineToUse.name}
                      </h3>
                      <span className={cn("rounded-full px-3 py-0.5 text-xs font-semibold", s.bg, s.text)}>
                        {s.label}
                      </span>
                    </div>
                  </div>

                  <div className="grid gap=4">
                    <div>
                      <p className="text-sm font-medium text-slate-700">Generic Name</p>
                      <p className="mt-1 text-slate-600 line-clamp-1">
                        {medicineToUse.genericName ?? "Not specified"}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-slate-700">Brand Name</p>
                      <p className="mt-1 text-slate-600 line-clamp-1">
                        {medicineToUse.brandName ?? "Not specified"}
                      </p>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm font-medium text-slate-700">Type</p>
                      <p className="mt-1 text-slate-600 capitalize">
                        {medicineToUse.type}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-slate-700">Quantity</p>
                      <p className="mt-1 text-slate-600">
                        {medicineToUse.quantity !== null ? `${medicineToUse.quantity} ${medicineToUse.quantityUnit ?? ""}` : "Not specified"}
                      </p>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm font-medium text-slate-700">Expiry Date</p>
                      <p className="mt-1 text-slate-600">
                        {medicineToUse.expiryDate ? new Date(medicineToUse.expiryDate).toLocaleDateString() : "Not specified"}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-slate-700">Purchase Date</p>
                      <p className="mt-1 text-slate-600">
                        {medicineToUse.purchaseDate ? new Date(medicineToUse.purchaseDate).toLocaleDateString() : "Not specified"}
                      </p>
                    </div>
                  </div>

                  {medicineToUse.notes && (
                    <div className="mt-4">
                      <p className="text-sm font-medium text-slate-700 mb-1">Notes</p>
                      <p className="text-slate-600">{medicineToUse.notes}</p>
                    </div>
                  )}
                </>
              )}
            </div>
          )}
        </div>

        <div className="pt-4">
          {!isCreate && (
            <>
              <button
                type="button"
                onClick={() => setEditMode(true)}
                className="w-full flex items-center justify-center px-4 py-2 rounded-md border border-transparent bg-brand-500 text-white hover:bg-brand-600"
              >
                Edit Medicine
              </button>
              <button
                type="button"
                onClick={handleDelete}
                className="mt-2 w-full flex items-center justify-center px-4 py-2 rounded-md border border-transparent bg-red-500 text-white hover:bg-red-600"
              >
                Delete Medicine
              </button>
            </>
          )}
        </div>
      </div>
    </>
  );
}