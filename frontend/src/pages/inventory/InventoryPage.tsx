import { useState } from "react";
import { PageIntro } from "@/components/common/PageIntro";
import { Input } from "@/components/common/Input";
import { Button } from "@/components/common/Button";
import { Card } from "@/components/common/Card";
import { EmptyState } from "@/components/common/EmptyState";
import { LoadingScreen } from "@/components/common/LoadingScreen";
import { InlineError } from "@/components/feedback/InlineError";
import { useInventory } from "@/hooks/useInventory";
import { Package } from "lucide-react";
import type { InventoryCreateRequest } from "@/types/api";

export function InventoryPage() {
  const {
    inventory,
    loading,
    error,
    success,
    createInventory,
  } = useInventory();

  const [formData, setFormData] = useState<InventoryCreateRequest>({
    medicine_id: null,
    name: "",
    generic_name: null,
    brand_name: null,
    type: "tablet",
    quantity: null,
    quantity_unit: null,
    expiry_date: null,
    purchase_date: null,
    image_path: null,
    notes: null,
  });

  const [copySuccess, setCopySuccess] = useState(false);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => {
    const target = e.target;
    const { name, type } = target;

    let value: any;

    if (type === "checkbox") {
      value = (target as HTMLInputElement).checked;
    } else if (type === "number") {
      const numValue = target.value;
      value = numValue === "" ? null : Number(numValue);
    } else {
      value = target.value;
    }

    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await createInventory(formData);
    // reset form
    setFormData({
      medicine_id: null,
      name: "",
      generic_name: null,
      brand_name: null,
      type: "tablet",
      quantity: null,
      quantity_unit: null,
      expiry_date: null,
      purchase_date: null,
      image_path: null,
      notes: null,
    });
  };

  return (
    <>
      <PageIntro
        eyebrow="Inventory"
        title="Manage Inventory"
        description="Add, view, and manage your medical inventory."
      />
      {success && (
        <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg text-green-800">
          {success}
          {!copySuccess && (
            <Button
              variant="secondary"
              size="sm"
              onClick={() => {
                navigator.clipboard.writeText(success);
                setCopySuccess(true);
                setTimeout(() => setCopySuccess(false), 2000);
              }}
            >
              {copySuccess ? "Copied!" : "Copy"}
            </Button>
          )}
        </div>
      )}
      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-800">
          <InlineError title="Error" message={error} />
        </div>
      )}
      <div className="space-y-6">
        <Card>
          <h2 className="mb-4 text-lg font-semibold text-slate-900">
            Add Inventory Item
          </h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <Input
                  label="Medicine ID (optional)"
                  name="medicine_id"
                  type="number"
                  value={formData.medicine_id ?? ""}
                  onChange={handleChange}
                  className="mb-2"
                />
              </div>
              <div>
                <Input
                  label="Name"
                  name="name"
                  type="text"
                  value={formData.name ?? ""}
                  onChange={handleChange}
                  className="mb-2"
                />
              </div>
              <div>
                <Input
                  label="Generic Name (optional)"
                  name="generic_name"
                  type="text"
                  value={formData.generic_name ?? ""}
                  onChange={handleChange}
                  className="mb-2"
                />
              </div>
              <div>
                <Input
                  label="Brand Name (optional)"
                  name="brand_name"
                  type="text"
                  value={formData.brand_name ?? ""}
                  onChange={handleChange}
                  className="mb-2"
                />
              </div>
              <div>
                <label className="block mb-1 font-medium text-slate-900">
                  Medicine Type
                </label>
                <select
                  name="type"
                  value={formData.type}
                  onChange={handleChange}
                  className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                >
                  {["tablet", "capsule", "syrup", "cream", "injection", "ointment", "drops", "inhaler", "other"].map(
                    (value) => (
                      <option key={value} value={value}>
                        {value.charAt(0).toUpperCase() + value.slice(1)}
                      </option>
                    )
                  )}
                </select>
              </div>
              <div>
                <Input
                  label="Quantity (optional)"
                  name="quantity"
                  type="number"
                  value={formData.quantity ?? ""}
                  onChange={handleChange}
                  className="mb-2"
                />
              </div>
              <div>
                <Input
                  label="Quantity Unit (optional)"
                  name="quantity_unit"
                  type="text"
                  value={formData.quantity_unit ?? ""}
                  onChange={handleChange}
                  className="mb-2"
                />
              </div>
              <div>
                <Input
                  label="Expiry Date (optional)"
                  name="expiry_date"
                  type="date"
                  value={formData.expiry_date ?? ""}
                  onChange={handleChange}
                  className="mb-2"
                />
              </div>
              <div>
                <Input
                  label="Purchase Date (optional)"
                  name="purchase_date"
                  type="date"
                  value={formData.purchase_date ?? ""}
                  onChange={handleChange}
                  className="mb-2"
                />
              </div>
              <div>
                <Input
                  label="Notes (optional)"
                  name="notes"
                  type="text"
                  value={formData.notes ?? ""}
                  onChange={handleChange}
                  className="mb-2"
                />
              </div>
            </div>

            <Button type="submit" variant="primary" disabled={loading}>
              {loading ? "Adding..." : "Add to Inventory"}
            </Button>
          </form>
        </Card>

        <Card>
          <h2 className="mb-4 text-lg font-semibold text-slate-900">
            Inventory List ({inventory.length})
          </h2>
          {loading && inventory.length === 0 ? (
            <LoadingScreen
              title="Loading inventory…"
              description="Please wait while we load your inventory."
            />
          ) : error ? (
            <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-800">
              <InlineError title="Load error" message={error} />
            </div>
          ) : inventory.length === 0 ? (
            <EmptyState
              icon={Package}
              title="Inventory is empty"
              description="Add your first inventory item using the form above."
            />
          ) : (
            <div className="space-y-4">
              {inventory.map((item) => (
                <div
                  key={item.id}
                  className="p-4 bg-slate-50 border border-slate-200 rounded-lg"
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="font-medium text-slate-900">
                        {item.name || "Unnamed"}
                      </h3>
                      <p className="text-sm text-slate-600">
                        Type: {item.type}
                      </p>
                      {item.quantity !== null && (
                        <p className="text-sm text-slate-600">
                          Quantity: {item.quantity} {item.quantity_unit || ""}
                        </p>
                      )}
                      {item.expiry_date && (
                        <p className="text-sm text-slate-600">
                          Expires:{" "}
                            {new Date(item.expiry_date).toLocaleDateString()}
                        </p>
                      )}
                    </div>
                    <div className="text-xs text-slate-500">
                      {item.status}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>
      </div>
    </>
  );
}