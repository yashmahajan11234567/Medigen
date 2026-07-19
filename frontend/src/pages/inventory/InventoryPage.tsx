import { useState } from "react";
import { Pill } from "lucide-react";
import { cn } from "@/lib/cn";
import { MedicineGrid } from "@/pages/inventory/components/MedicineGrid";
import { MedicineDrawer } from "@/pages/inventory/components/MedicineDrawer";
import { useToast } from "@/components/ui/ToastProvider";
import type { MedicineItem } from "@/pages/inventory/components/MedicineGrid";
import { useInventory } from "@/hooks/useInventory";

export function InventoryPage() {
  const {
    inventory: medicines,
    refresh,
    createMedicine,
    updateMedicine,
    deleteMedicine,
  } = useInventory();
  const { addToast } = useToast();
  const [selectedMedicine, setSelectedMedicine] = useState<MedicineItem | null>(
    null
  );
  const [searchTerm, setSearchTerm] = useState("");

  const handleRefresh = async () => {
    await refresh();
    addToast({
      title: "Inventory refreshed.",
      description: "Your inventory has been updated.",
      variant: "success",
    });
  };

  const handleCreate = async (data: any) => {
    // Convert camelCase to snake_case for API
    const apiData = {
      name: data.name,
      generic_name: data.generic_name,
      brand_name: data.brand_name,
      type: data.type,
      quantity: data.quantity,
      quantity_unit: data.quantity_unit,
      expiry_date: data.expiry_date,
      purchase_date: data.purchase_date,
      image_path: data.image_path,
      notes: data.notes,
    };
    await createMedicine(apiData);
    setSearchTerm("");
    addToast({
      title: "Medicine added.",
      description: "The medicine has been added to your inventory.",
      variant: "success",
    });
  };

  const handleUpdate = async (id: number, data: any) => {
    // Convert camelCase to snake_case for API
    const apiData = {
      name: data.name,
      gender_name: data.gender_name,
      brand_name: data.brand_name,
      type: data.type,
      quantity: data.quantity,
      quantity_unit: data.quantity_unit,
      expiry_date: data.expiry_date,
      purchase_date: data.purchase_date,
      image_path: data.image_path,
      notes: data.notes,
    };
    await updateMedicine(id, apiData);
    setSelectedMedicine(null);
    addToast({
      title: "Medicine updated.",
      description: "The medicine has been updated.",
      variant: "success",
    });
  };

  const handleDelete = async (id: number) => {
    await deleteMedicine(id);
    setSelectedMedicine(null);
    addToast({
      title: "Medicine removed.",
      description: "The medicine has been removed from your inventory.",
      variant: "success",
    });
  };

  const filtered = medicines
    .filter(
      (m) =>
        m.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (m.generic_name &&
          m.generic_name
            .toLowerCase()
            .includes(searchTerm.toLowerCase()))
    )
    .map((item) => ({
      id: item.id,
      name: item.name ?? "",
      genericName: item.generic_name ?? "",
      brandName: item.brand_name ?? "",
      type: item.type ?? "tablet",
      quantity: item.quantity ?? 0,
      unit: item.unit ?? "",
      expiryDate: item.expiry_date ?? "",
      storageInstructions: "", // Not available from API
      notes: item.notes ?? "",
      // Map inventory status to medicine status
      status:
        item.status === "available"
          ? "healthy"
          : item.status === "low_stock"
          ? "low"
          : item.status === "expiring_soon"
          ? "expiring"
          : item.status === "expired"
          ? "expired"
          : "low", // out_of_stock -> low
    }));

  return (
    <div className="p-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6">
        <h1 className="text-2xl font-bold text-slate-900">
          Medicine Inventory
        </h1>
        <div className="flex items-center gap-4">
          <input
            type="text"
            placeholder="Search medicines..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="flex-1 min-w-[200px] px-4 py-2 rounded-border border-slate-200 focus:ring-2 focus:ring-brand-200"
          />
          <button
            onClick={handleRefresh}
            className="flex items-center justify-center px-4 py-2 rounded-md border border-transparent bg-brand-500 text-white hover:bg-brand-600"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="mr-2 h-4 w-4"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={1.5}
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 10h16M4 14h16M4 18h16" />
            </svg>
            Refresh
          </button>
          <button
            onClick={() => setSelectedMedicine(null)}
            className="flex items-center justify-center px-4 py-2 rounded-md border border-transparent bg-brand-500 text-white hover:bg-brand-600"
          >
            <Pill className="mr-2 h-4 w-4" />
            Add Medicine
          </button>
        </div>
      </div>

      <MedicineGrid medicines={filtered} onSelect={setSelectedMedicine} />

      {selectedMedicine && (
        <MedicineDrawer
          medicine={selectedMedicine}
          onClose={() => setSelectedMedicine(null)}
          onUpdate={handleUpdate}
          onDelete={handleDelete}
        />
      )}
    </div>
  );
}