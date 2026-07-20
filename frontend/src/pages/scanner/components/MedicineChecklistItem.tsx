import { useEffect, useState } from "react";
import { MedicineType } from "@/types/api";

export interface MedicineChecklistItem {
  id: string;
  medicineId: number | null;
  medicineName: string;
  genericName: string | null;
  brandName: string | null;
  type?: MedicineType;
  quantity: number;
  quantityUnit: string | null;
  expiryDate: string | null;
  isSelected: boolean;
}

export interface MedicineChecklistItemProps {
  /** Unique id for the medicine row */
  id: string;
  /** The medicine data to display */
  medicine: {
    /** ID in the global Medicine table (null if unknown) */
    medicineId: number | null;
    /** Original extracted name (always present) */
    name: string;
    /** Generic name if known (null if unknown) */
    genericName: string | null;
    /** Brand name if known (null if unknown) */
    brandName: string | null;
    /** Matched medicine type (e.g., 'tablet', 'capsule', etc.) */
    type?: MedicineType;
    /** Quantity to add to inventory */
    quantity?: string;
    /** Unit of measurement */
    quantityUnit?: string;
    /** Expiry date (YYYY-MM-DD) */
    expiryDate?: string;
  };
  /** Toggle selection */
  onToggle: (id: string) => void;
  /** Select all */
  onSelectAll: () => void;
  /** Clear all */
  onClearAll: () => void;
  /** Edit field action */
  onEdit: (id: string, field: string, value: string) => void;
  /** Lookup unknown medicine by edited name */
  onLookup: (id: string) => void;
  /** Submit this row to inventory */
  onSubmit: (item: MedicineChecklistItem) => Promise<void> | void;
  /** Resolve duplicate with action */
  onResolveDuplicate: (item: MedicineChecklistItem, action: "update" | "skip" | "separate") => void;
  /** Submit all selected items */
  onSubmitAll: () => void;
  /** Current submission status */
  isSubmitting: boolean;
  /** Known vs unknown flag */
  isKnown: boolean;
  /** Duplicate flag */
  isDuplicate: boolean;
  /** Current edit field */
  editField?: string;
  /** Current edit value */
  editValue?: string;
  /** Error message */
  error?: string;
  /** Random string ID for React */
  randomId: string;
}

export default function MedicineChecklistItem({
  id,
  medicine,
  onToggle,
  onSelectAll,
  onClearAll,
  onEdit,
  onLookup,
  onSubmit,
  onResolveDuplicate,
  onSubmitAll,
  isSubmitting,
  isKnown,
  isDuplicate,
  editField,
  editValue,
  error,
  randomId,
}: MedicineChecklistItemProps) {
  const [showLookup, setShowLookup] = useState(false);
  const [editFieldLocal, setEditFieldLocal] = useState<string>(editField ?? "");
  const [editValueLocal, setEditValueLocal] = useState<string>(editValue ?? "");
  const [isEditing, setIsEditing] = useState<boolean>(!!editFieldLocal);

  // Quantity, unit, expiry state
  const [quantity, setQuantity] = useState<string>("");
  const [unit, setUnit] = useState<string>("");
  const [expiryDate, setExpiryDate] = useState<string>("");
  const [quantityError, setQuantityError] = useState<string>("");
  const [unitError, setUnitError] = useState<string>("");
  const [expiryError, setExpiryError] = useState<string>("");

  // Unknown medicine confirmation dialog
  const [showConfirmUnknown, setShowConfirmUnknown] = useState<boolean>(false);
  const [confirmationApproved, setConfirmationApproved] = useState<boolean>(false);

  // Validation helper functions
  const validateQuantity = () => {
    const val = parseInt(quantity, 10);
    if (!quantity) return "Quantity is required";
    if (isNaN(val) || val <= 0) return "Quantity must be > 0";
    setQuantityError("");
    return "";
  };

  const validateUnit = () => {
    if (!unit) {
      setUnitError("Unit is required");
      return false;
    }
    setUnitError("");
    return true;
  };

  const validateExpiry = () => {
    // Simple YYYY-MM-DD format check
    if (!expiryDate) {
      setExpiryError("Expiry date is required");
      return false;
    }
    const dateParts = expiryDate.split("-");
    if (
      dateParts.length === 3 &&
      dateParts[0].length === 4 &&
      dateParts[1].length === 2 &&
      dateParts[2].length === 2
    ) {
      const year = parseInt(dateParts[0], 10);
      const month = parseInt(dateParts[1], 10);
      const day = parseInt(dateParts[2], 10);
      if (
        year >= 1900 &&
        month >= 1 &&
        month <= 12 &&
        day >= 1 &&
        day <= 31
      ) {
        setExpiryError("");
        return true;
      }
    }
    setExpiryError("Invalid date format (YYYY-MM-DD)");
    return false;
  };

  const validateAllFields = () => {
    const qtyErr = validateQuantity();
    const unitOk = validateUnit();
    const expiryOk = validateExpiry();
    return qtyErr === "" && unitOk && expiryOk;
  };

  const handleQuantityChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setQuantity(e.target.value);
    if (e.target.value) {
      const err = validateQuantity();
      setQuantityError(err);
    }
  };

  const handleUnitChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setUnit(e.target.value);
    if (e.target.value) {
      const ok = validateUnit();
      setUnitError(ok ? "" : "Unit is required");
    }
  };

  const handleExpiryChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setExpiryDate(e.target.value);
    if (e.target.value) {
      const ok = validateExpiry();
      setExpiryError(ok ? "" : "Invalid date format");
    }
  };

  const handleEditChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setEditValueLocal(e.target.value);
  };

  const handleBlurEdit = () => {
    if (editField) {
      onEdit(id, editField, editValueLocal);
      setIsEditing(false);
      setEditFieldLocal("");
      setEditValueLocal("");
    }
  };

  // Called when user clicks "Add to Inventory" on this row
  const maybeSubmit = async () => {
    // Validate required fields first
    const qtyErr = validateQuantity();
    if (qtyErr) setQuantityError(qtyErr);
    const unitOk = validateUnit();
    if (!unitOk) setUnitError("Unit is required");
    const expiryOk = validateExpiry();
    if (!expiryOk) setExpiryError("Invalid expiry date");

    // If any validation errors, do not proceed
    if (quantityError || !unitOk || !expiryOk) return;

    // If medicine is unknown, show confirmation dialog
    if (!isKnown) {
      setShowConfirmUnknown(true);
      return;
    }

    // All good, submit the item
    const payload = {
      id,
      medicineId: medicine.medicineId,
      medicineName: medicine.name,
      genericName: medicine.genericName,
      brandName: medicine.brandName,
      type: medicine.type,
      quantity: parseInt(quantity, 10),
      quantityUnit: unit,
      expiryDate: expiryDate,
      isSelected: true,
    };
    onSubmit(payload);
  };

  // Handle unknown confirmation dialog actions
  const handleCreateAnyway = () => {
    setShowConfirmUnknown(false);
    maybeSubmit();
  };

  const handleGoBack = () => {
    setShowConfirmUnknown(false);
  };

  useEffect(() => {
    if (editField) {
      setEditFieldLocal(editField);
      setEditValueLocal(editValue ?? "");
      setIsEditing(true);
    }
  }, [editField, editValue]);

  const medicineBadgeLabel = isKnown ? "Known" : "Unknown";
  const badgeColor = isKnown ? "text-green-700 bg-green-50" : "text-amber-700 bg-amber-50";

  const quantityIsValid = quantityError === "";
  const unitIsValid = unitError === "";
  const expiryIsValid = expiryError === "";

  return (
    <div className="rounded-xl border border-slate-100 bg-white p-4 space-y-4">
      {/* Top row: checkbox + name + badge */}
      <div className="flex items-center gap-3">
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={true}
            onChange={() => onToggle(id)}
            className="h-4 w-4 rounded border-slate-300 text-brand-600 focus:ring-brand-500"
            autoComplete="off"
          />
          <span className="text-sm text-slate-600 whitespace-nowrap">{medicine.name}</span>
        </label>

        <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ${badgeColor}`}>
          {medicineBadgeLabel}
        </span>

        {isDuplicate && (
          <span className="inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium bg-rose-50 text-rose-700">
            Duplicate
          </span>
        )}
      </div>

      {/* Edit controls for unknown medicines */}
      {!isKnown && (
        <div className="flex flex-wrap items-center gap-2">
          <select
            onChange={(e) => {
              onEdit(id, "type", e.target.value as MedicineType);
              setIsEditing(false);
            }}
            className="h-9 rounded-lg border border-slate-200 bg-white px-3 text-sm text-slate-700"
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

          <input
            type="text"
            placeholder="Edit name"
            value={editValueLocal}
            onChange={handleEditChange}
            onBlur={handleBlurEdit}
            className="h-9 rounded-lg border border-slate-200 bg-white px-3 text-sm text-slate-700"
          />

          {isEditing && (
            <input
              type="text"
              placeholder="Edit name"
              value={editValueLocal}
              onChange={handleEditChange}
              onBlur={handleBlurEdit}
              className="h-9 rounded-lg border border-slate-200 bg-white px-3 text-sm text-slate-700"
            />
          )}

          <button
            className="h-9 rounded-lg bg-slate-100 px-3 text-sm text-slate-600 hover:bg-slate-200"
            onClick={() => setShowLookup(true)}
          >
            Look Up
          </button>

          {showLookup && (
            <input
              type="text"
              placeholder="Search..."
              value={editValueLocal}
              onChange={(e) => setEditValueLocal(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  onLookup(id);
                  setShowLookup(false);
                }
              }}
              className="h-9 w-48 rounded-lg border border-slate-200 bg-white px-3 text-sm text-slate-700"
            />
          )}
        </div>
      )}

      {/* Quantity inputs - always show when not submitting */}
      {!isSubmitting && (
        <div className="flex flex-wrap items-center gap-2">
          <input
            type="text"
            placeholder="Quantity"
            value={quantity}
            onChange={handleQuantityChange}
            className="h-9 w-20 rounded-lg border border-slate-200 bg-white px-3 text-sm text-slate-700"
            disabled={isSubmitting}
          />
          {quantityError && (
            <span className="text-sm text-red-600">{quantityError}</span>
          )}
          <input
            type="text"
            placeholder="Unit"
            value={unit}
            onChange={handleUnitChange}
            className="h-9 w-20 rounded-lg border border-slate-200 bg-white px-3 text-sm text-slate-700"
            disabled={isSubmitting}
          />
          {unitError && (
            <span className="text-sm text-red-600">{unitError}</span>
          )}
          <input
            type="date"
            placeholder="Expiry"
            value={expiryDate}
            onChange={handleExpiryChange}
            className="h-9 w-36 rounded-lg border border-slate-200 bg-white px-3 text-sm text-slate-700"
            disabled={isSubmitting}
          />
          {expiryError && (
            <span className="text-sm text-red-600">{expiryError}</span>
          )}
        </div>
      )}

      {/* Duplicate actions */}
      {isDuplicate && (
        <div className="flex flex-wrap gap-2">
          <button
            className="h-9 rounded-lg bg-slate-100 px-3 text-sm text-slate-600 hover:bg-slate-200"
            onClick={() => onResolveDuplicate(
              { id, medicineId: medicine.medicineId, medicineName: medicine.name, genericName: medicine.genericName, brandName: medicine.brandName, type: medicine.type, quantity: parseInt(quantity, 10) || 0, quantityUnit: unit, expiryDate, isSelected: true },
              "update"
            )}
          >
            Update Qty
          </button>
          <button
            className="h-9 rounded-lg bg-slate-100 px-3 text-sm text-slate-600 hover:bg-slate-200"
            onClick={() => onResolveDuplicate(
              { id, medicineId: medicine.medicineId, medicineName: medicine.name, genericName: medicine.genericName, brandName: medicine.brandName, type: medicine.type, quantity: parseInt(quantity, 10) || 0, quantityUnit: unit, expiryDate, isSelected: true },
              "skip"
            )}
          >
            Skip
          </button>
          <button
            className="h-9 rounded-lg bg-slate-100 px-3 text-sm text-slate-600 hover:bg-slate-200"
            onClick={() => onResolveDuplicate(
              { id, medicineId: medicine.medicineId, medicineName: medicine.name, genericName: medicine.genericName, brandName: medicine.brandName, type: medicine.type, quantity: parseInt(quantity, 10) || 0, quantityUnit: unit, expiryDate, isSelected: true },
              "separate"
            )}
          >
            Separate Entry
          </button>
        </div>
      )}

      {/* Submit button */}
      {!isSubmitting && (
        <button
          onClick={maybeSubmit}
          className="h-10 rounded-2xl bg-brand-600 px-5 text-sm font-semibold text-white shadow-sm hover:bg-brand-700 disabled:opacity-60"
        >
          Add to Inventory
        </button>
      )}

      {/* Unknown medicine confirmation dialog */}
      {showConfirmUnknown && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50" onClick={handleGoBack}>
          <div className="mx-4 w-full max-w-md rounded-2xl bg-white p-6 shadow-xl" onClick={(e) => e.stopPropagation()}>
            <div className="mb-4 text-lg font-semibold text-slate-900">Unknown Medicine</div>
            <p className="text-sm text-slate-600">
              This medicine was not found in the MediGen database.
              Creating a new medicine record may affect future searches.
            </p>
            <div className="mt-6 flex justify-end gap-3">
              <button
                onClick={handleGoBack}
                className="h-10 rounded-2xl bg-slate-100 px-5 text-sm font-medium text-slate-700 hover:bg-slate-200"
              >
                Go Back
              </button>
              <button
                onClick={handleCreateAnyway}
                className="h-10 rounded-2xl bg-rose-600 px-5 text-sm font-semibold text-white hover:bg-rose-700"
              >
                Create Anyway
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Error display */}
      {error && <div className="text-sm text-red-600">{error}</div>}

      {/* Loading spinner */}
      {isSubmitting && (
        <div className="flex items-center gap-2 text-sm text-slate-500">
          Processing...
        </div>
      )}
    </div>
  );
}