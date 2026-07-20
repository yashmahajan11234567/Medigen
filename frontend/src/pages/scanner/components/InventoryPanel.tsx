import MedicineChecklistItemComponent from "./MedicineChecklistItem";
import { MedicineChecklistItemProps } from "./MedicineChecklistItem";
import { MedicineChecklistItem } from "./MedicineChecklistItem";
import { useMemo } from "react";
import type { MedicineForInventory } from "@/types/api";

interface InventoryPanelProps {
  items: MedicineForInventory[];
  onToggle: (id: string) => void;
  onSelectAll: () => void;
  onClearAll: () => void;
  onEdit: (id: string, field: string, value: string) => void;
  onLookup: (id: string) => void;
  onSubmit: (item: MedicineForInventory) => Promise<void>;
  onSubmitAll: () => void;
  isSubmitting: boolean;
  onResolveDuplicate: (item: MedicineChecklistItem, action: "update" | "skip" | "separate") => void;
  error?: string;
}

export default function InventoryPanel({
  items,
  onToggle,
  onSelectAll,
  onClearAll,
  onEdit,
  onLookup,
  onSubmit,
  isSubmitting,
  onResolveDuplicate,
  onSubmitAll,
  error,
}: InventoryPanelProps) {
  const inventoryItems = useMemo(() => items, [items]);

  const selectedCount = useMemo(() => inventoryItems.filter(i => i.isSelected).length, [inventoryItems]);

  return (
    <div className="space-y-6 border-t-2 border-brand-200 pb-6 pt-4">
      {/* Header with controls */}
      <div className="flex items-start justify-between">
        <div className="flex gap-2">
          <button
            onClick={onSelectAll}
            className="h-9 rounded-2xl bg-brand-600 px-4 text-sm font-semibold text-white hover:bg-brand-700 disabled:opacity-60"
            disabled={isSubmitting}
          >
            Select All ({items.length})
          </button>
          <button
            onClick={onClearAll}
            className="h-9 rounded-2xl bg-white px-4 text-sm font-medium text-slate-700 ring-1 ring-slate-200 hover:bg-slate-50 disabled:opacity-60"
            disabled={isSubmitting}
          >
            Clear All
          </button>
        </div>
        <span className="text-sm font-medium text-slate-900">
          {selectedCount} of {items.length} selected
        </span>
      </div>

      <hr className="border-slate-100" />

      {/* List of medicine rows */}
      <ul className="space-y-3">
        {inventoryItems.map((item) => {
          const medicine: MedicineChecklistItemProps['medicine'] = {
            medicineId: item.medicineId,
            name: item.name,
            genericName: item.genericName,
            brandName: item.brandName,
            type: item.type,
            quantity: item.quantity !== null ? String(item.quantity) : undefined,
            quantityUnit: item.quantityUnit === null ? undefined : item.quantityUnit,
            expiryDate: item.expiryDate === null ? undefined : item.expiryDate,
          };

          const itemProps = {
            id: item.id,
            medicine,
            onToggle: onToggle,
            onSelectAll: onSelectAll,
            onClearAll: onClearAll,
            onEdit: onEdit,
            onLookup: onLookup,
            onSubmit: (_itemArg: MedicineChecklistItem) => {
              return onSubmit(item);
            },
            onResolveDuplicate: onResolveDuplicate,
            onSubmitAll: onSubmitAll,
            isSubmitting: isSubmitting,
            isKnown: item.isKnown,
            isDuplicate: item.isDuplicate,
            editField: undefined,
            editValue: undefined,
            error: item.error === null ? undefined : item.error,
            randomId: item.id + Math.random().toString(36).substr(2, 9),
          } as MedicineChecklistItemProps;

          return <MedicineChecklistItemComponent key={item.id} {...itemProps} />;
        })}
      </ul>

      {/* Submit button */}
      {!isSubmitting && (
        <button
          onClick={onSubmitAll}
          className="h-11 rounded-2xl bg-brand-600 px-6 text-sm font-semibold text-white shadow-sm hover:bg-brand-700"
        >
          Add Selected to Inventory
        </button>
      )}

      {/* Global error */}
      {error && (
        <div className="text-sm text-red-600">
          {error}
        </div>
      )}
    </div>
  );
}