import { useState, useEffect } from "react";
import { PageIntro } from "@/components/common/PageIntro";
import { Input } from "@/components/common/Input";
import { Button } from "@/components/common/Button";
import { Card } from "@/components/common/Card";
import { EmptyState } from "@/components/common/EmptyState";
import { LoadingScreen } from "@/components/common/LoadingScreen";
import { InlineError } from "@/components/feedback/InlineError";
import { useGenericFinder } from "@/hooks/useGenericFinder";
import { Medicine } from "@/types/api";
import { Search as SearchIcon, Pill as PillIcon } from "lucide-react";

export function GenericFinderPage() {
  const {
    searchTerm,
    setSearchTerm,
    results,
    selectedMedicine,
    loading,
    error,
    success,
    selectMedicine,
    addToInventory,
  } = useGenericFinder();

  const [copySuccess, setCopySuccess] = useState(false);

  const handleSearch = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
  };

  return (
    <>
      <PageIntro
        title="Generic Finder"
        subtitle="Search for medicines by brand name and add generic equivalents to your inventory."
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
              type="text"
              placeholder="Search by brand name (e.g., Amoxil)"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="mb-2"
            />
            <Button type="submit" variant="primary" disabled={loading}>
              {loading ? "Searching..." : "Search"}
            </Button>
          </form>

          {loading && results.length === 0 && (
            <LoadingScreen message="Searching for medicines..." />
          )}

          {error && (
            <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-800">
              <InlineError>{error}</InlineError>
            </div>
          )}

          {results.length > 0 && !loading && !error && (
            <Card className="h-full">
              <h2 className="mb-3 text-lg font-semibold text-slate-900">
                Search Results ({results.length})
              </h2>
              <div className="space-y-2">
                {results.map((medicine) => (
                  <Button
                    key={medicine.id}
                    variant="ghost"
                    className="w-full text-left p-3 hover:bg-slate-50 border border-slate-200 rounded-lg"
                    onClick={() => selectMedicine(medicine)}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="font-medium text-slate-900">{medicine.name}</h3>
                        <p className="text-sm text-slate-500">{medicine.composition}</p>
                      </div>
                      <div className="text-slate-400">
                        {medicine.exact_matches.length > 0 ? (
                          <span className="px-2 py-0.5 bg-green-100 text-green-800 text-xs rounded">
                            {medicine.exact_matches.length} generic
                          </span>
                        ) : (
                          <span className="text-xs italic">No generics</span>
                        )}
                      </div>
                    </div>
                  </Button>
                ))}
              </div>
            </Card>
          )}

          {(results.length === 0 && !loading && !error && searchTerm.length > 0) && (
            <EmptyState
              icon="Search"
              title="No medicines found"
              description="Try a different search term or check the spelling."
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
                  <h3 className="font-medium text-slate-900">{selectedMedicine.name}</h3>
                  <p className="text-sm text-slate-500">{selectedMedicine.composition}</p>
                </div>

                {selectedMedicine.exact_matches.length > 0 ? (
                  <>
                    <h3 className="mb-2 text-font-semibold text-slate-800">
                      Exact Generic Matches
                    </h3>
                    <div className="space-y-2">
                      {selectedMedicine.exact_matches.map((generic) => (
                        <Card
                          key={generic.id}
                          className="p-3 bg-green-50 border border-green-200"
                        >
                          <div className="flex justify-between items-start">
                            <div>
                              <h4 className="font-medium text-slate-900">{generic.name}</h4>
                  <p className="text-sm text-slate-500">{generic.composition}</p>
                            </div>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => addToInventory(generic.id)}
                              disabled={loading}
                              className="mt-2"
                            >
                              {loading ? "Adding..." : "Add to Inventory"}
                            </Button>
                          </div>
                        </Card>
                      ))}
                    </div>
                  </>
                ) : (
                  <p className="text-slate-500 italic">
                    No exact generic matches found for this medicine.
                  </p>
                )}
              </div>
            </Card>
          ) : (
            <EmptyState
              icon="Prescription"
              title="Select a medicine"
              description="Search for a medicine above to see its details and generic options."
            />
          )}
        </div>
      </div>
    </>
  );
}
