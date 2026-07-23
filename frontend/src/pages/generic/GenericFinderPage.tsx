import { useState } from "react";
import { PageIntro } from "@/components/common/PageIntro";
import { Input } from "@/components/common/Input";
import { Button } from "@/components/common/Button";
import { Card } from "@/components/common/Card";
import { EmptyState } from "@/components/common/EmptyState";
import { LoadingScreen } from "@/components/common/LoadingScreen";
import { InlineError } from "@/components/feedback/InlineError";
import { useGenericFinder } from "@/hooks/useGenericFinder";
import { Search as SearchIcon, Pill as PillIcon } from "lucide-react";

export function GenericFinderPage() {
  {
    searchTerm,
    setSearchTerm,
    results,
    selectedMedicine,
    loading,
    error,
    success,
    selectMedicine,
    addToInventory,
    apiMessage,
  } = useGenericFinder();

  const [copySuccess, setCopySuccess] = useState(false);

  const handleSearch = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
  };

  return (
    <>
      <PageIntro
        eyebrow="Generic Finder"
        title="Search Medicines"
        description="Find generic equivalents and add them to your inventory."
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
      <div className="grid gap-6 md:grid-cols-[1fr_2fr]">
        {/* Search and Results Column */}
        <div>
          <form onSubmit={handleSearch} className="mb-4">
            <Input
              label="Brand Name"
              placeholder="Enter brand name (e.g., Amoxil)"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="mb-2"
            />
            <Button type="submit" variant="primary" disabled={loading}>
              {loading ? "Searching..." : "Search"}
            </Button>
          </form>

          {loading && results.length === 0 && (
            <LoadingScreen
              title="Searching for medicines…"
              description="Please wait while we search the database."
            />
          )}

          {error && (
            <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-800">
              <InlineError title="Search error" message={error} />
            </div>
          )}

          {results.length > 0 && !loading && !error && (
            <Card className="h-full">
              <h2 className="mb-3 text-lg font-semibold text-slate-900">
                Generic Matches ({results.length})
              </h2>
              <div className="space-y-2">
                {results.map((med) => (
                  <Button
                    key={med.id}
                    variant="ghost"
                    className="w-full text-left p-3 hover:bg-slate-50 border border-slate-200 rounded-lg"
                    onClick={() => selectMedicine(med)}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="font-medium text-slate-900">{med.name}</h4>
                        {med.generic_name && (
                          <p className="text-sm text-slate-600">
                            Generic: {med.generic_name}
                          </p>
                        )}</div>
                      <div className="text-xs text-slate-500">
                        {med.composition.ingredient} {med.composition.strength} {med.composition.unit}
                      </div>
                    </div>
                  </Button>
                ))}
              </div>
            </Card>
          )}

          {(results.length === 0 && !loading && !error && searchTerm.length > 0) && (
            <EmptyState
              icon={SearchIcon}
              title="No medicines found"
              description={apiMessage ?? "Try a different search term or check the spelling."}
            />
          )}
        </div>

        {/* Details Column */}
        <div>
          {selectedMedicine ? (
            <Card>
              <h2 className="mb-4 text-lg font-semibold text-slate-900">
                Medicine Details
              </h2>
              <div className="space-y-4">
                <div className="space-y-2">
                  <h3 className="font-medium text-slate-900">
                    {selectedMedicine.name}
                  </h3>
                  {selectedMedicine.generic_name && (
                    <p className="text-sm">
                      <strong>Generic Name:</strong> {selectedMedicine.generic_name}
                    </p>
                  )}
                  {selectedMedicine.brand_name && (
                    <p className="text-sm">
                      <strong>Brand Name:</strong> {selectedMedicine.brand_name}
                    </p>
                  )}
                  <p className="text-sm">
                    <strong>Composition:</strong>
                  </p>
                  <p className="ml-4 text-sm">
                    Ingredient: {selectedMedicine.composition.ingredient}<br />
                    Strength: {selectedMedicine.composition.strength}<br />
                    Unit: {selectedMedicine.composition.unit}<br />
                    Dosage Form: {String(
                      selectedMedicine.composition.dosage_form
                    )}<br />
                    Route: {selectedMedicine.composition.route}
                  </p>
                  {/* Determine if generic */}
                  {(!selectedMedicine.brand_name ||
                    selectedMedicine.brand_name.trim() === "") && (
                    <p className="mt-2 text-sm text-green-600">
                      This is a generic medicine.
                    </p>
                  )}
                </div>

                <Button
                  variant="primary"
                  onClick={addToInventory}
                  className="w-full"
                  disabled={loading}
                >
                  {loading ? "Adding..." : "Add to Inventory"}
                </Button>
              </div>
            </Card>
          ) : (
            <EmptyState
              icon={PillIcon}
              title="Select a medicine"
              description="Choose a generic medicine from the search results to see its details and add to inventory."
            />
          )}
        </div>
      </div>
    </>
  );
}





