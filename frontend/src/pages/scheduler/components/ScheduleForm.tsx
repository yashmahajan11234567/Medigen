import { useState, useEffect } from "react";
import { Card } from "@/components/common/Card";
import { SectionTitle } from "@/pages/dashboard/components/SectionTitle";
import { DurationPicker } from "@/pages/scheduler/components/DurationPicker";
import { DosageSelector } from "@/pages/scheduler/components/DosageSelector";
import { DosageExplanation } from "@/pages/scheduler/components/DosageExplanation";
import { MealTimingSelector } from "@/pages/scheduler/components/MealTimingSelector";
import { ReminderPicker } from "@/pages/scheduler/components/ReminderPicker";
import { apiClient } from "@/lib/api-client";
import type { MedicineItem } from "@/pages/inventory/components/MedicineGrid";
import type { ScheduleCreateRequest } from "@/types/api";

interface ScheduleFormProps {
  onCreate: (schedule: ScheduleCreateRequest) => Promise<void>;
}

export function ScheduleForm({ onCreate }: ScheduleFormProps) {
  const [medicineName, setMedicineName] = useState("");
  const [duration, setDuration] = useState("7 Days");
  const [morning, setMorning] = useState(1);
  const [afternoon, setAfternoon] = useState(0);
  const [night, setNight] = useState(1);
  const [mealTiming, setMealTiming] = useState("After Meal");
  const [reminder, setReminder] = useState("08:00");
  const [notes, setNotes] = useState("");
  const [medicines, setMedicines] = useState<MedicineItem[]>([]);
  const [selectedMedicineId, setSelectedMedicineId] = useState<number | null>(null);
  const [loadingMedicines, setLoadingMedicines] = useState<boolean>(true);
  const [submitLoading, setSubmitLoading] = useState<boolean>(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});

  // Fetch medicines on mount
  useEffect(() => {
    const fetchMedicines = async () => {
      setLoadingMedicines(true);
      try {
        const response = await apiClient.get<{ items: MedicineItem[] }>(
          "/inventory"
        );
        setMedicines(response.data.items);
      } catch (err: any) {
        console.error("Failed to fetch medicines", err);
      } finally {
        setLoadingMedicines(false);
      }
    };

    fetchMedicines();
  }, []);

  const handleDosageChange = (
    slot: "morning" | "afternoon" | "night"
  ) => {
    if (slot === "morning") setMorning((v) => (v === 0 ? 1 : 0));
    if (slot === "afternoon") setAfternoon((v) => (v === 0 ? 1 : 0));
    if (slot === "night") setNight((v) => (v === 0 ? 1 : 0));
  };

  const handleSubmit = async () => {
    // Reset field errors
    setFieldErrors({});
    setSubmitError(null);

    // Validate medicine selection
    if (!selectedMedicineId) {
      setFieldErrors({ medicine: "Please select a medicine" });
      return;
    }

    // Parse duration to get number of days
    const durationMatch = duration.match(/^(\d+\s*Days$)/i);
    const durationDays = durationMatch ? parseInt(durationMatch[1], 10) : 7;

    // Convert mealTiming (e.g., "After Meal") to food_tyming (e.g., "after_food")
    const foodTymingValue = mealTiming
      .toLowerCase()
      .replace("meal", "food")
      .replace(" ", "_");

    // Prepare payload
    const payload: ScheduleCreateRequest = {
      medicine_id: selectedMedicineId,
      dosage_pattern: `${morning}-${afternoon}-${night}`,
      quantity: null,
      quantity_unit: null,
      start_date: new Date().toISOString().split("T")[0],
      end_date: null,
      purchase_date: null,
      expiry_date: null,
      duration_days: durationDays,
      food_tyming: foodTymingValue,
      reminder_times: null,
      notes: notes || null,
      source: "manual",
      pharmacy_name: null,
    };

    setSubmitLoading(true);
    try {
      await onCreate(payload);
      // Reset form after successful submission
      setMedicineName("");
      setDuration("7 Days");
      setMorning(1);
      setAfternoon(0);
      setNight(1);
      setMealTiming("After Meal");
      setReminder("08:00");
      setNotes("");
      setSelectedMedicineId(null);
    } catch (err: any) {
      if (err.response?.status === 422) {
        // Validation errors from backend
        const errors = err.response.data?.errors || {};
        setFieldErrors(errors);
        setSubmitError(
          Object.values(errors)
            .flat()
            .join(" ") || "Validation failed"
        );
      } else {
        setSubmitError(
          err.response?.data?.message ||
            err.message ||
            "Failed to create schedule"
        );
      }
    } finally {
      setSubmitLoading(false);
    }
  };

  return (
    <Card className="p-5 sm:p-6">
      <SectionTitle>Add Schedule</SectionTitle>

      {submitError && (
        <div className="mb-4 p-3 bg-red-50 text-red-700 rounded">
          {submitError}
        </div>
      )}

      <div className="mt-5 space-y-5">
        {/* Medicine Selection */}
        <div>
          <label className="mb-1.5 block text-sm font-medium text-slate-700">
            Medicine Name
          </label>
          <div className="relative">
            <input
              type="text"
              value={medicineName}
              onChange={(e) => setMedicineName(e.target.value)}
              placeholder="Search or type medicine name..."
              className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 placeholder-slate-400 shadow-soft transition focus:border-brand-300 focus:outline-none focus:ring-4 focus:ring-brand-100 pl-10 pr-4"
            />
            {loadingMedicines ? (
              <span className="absolute left-3 top-1/2 -translate-y-1/2 flex h-4 w-4 items-center justify-center">
                <svg className="animate-spin h-4 w-4 text-brand-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"></path>
                </svg>
              </span>
            ) : (
              <>
                {/* Dropdown list of medicines */}
                {medicines.length > 0 && (
                  <div className="absolute left-0 right-0 mt-2 w-full bg-white border border-slate-200 rounded-md shadow-lg z-10 max-h-60 overflow-y-auto">
                    {medicines
                      .filter(
                        (m) =>
                          mealTiming.trim() === "" ||
                          m.name
                            .toLowerCase()
                            .includes(mealTiming.toLowerCase())
                      )
                      .slice(0, 10)
                      .map((med) => (
                        <div
                          key={med.id}
                          onClick={() => {
                            setMedicineName(med.name);
                            setSelectedMedicineId(med.id);
                          }}
                          className="px-4 py-2 text-sm hover:bg-brand-50 cursor-pointer"
                        >
                          {med.name}
                          {med.genericName && (
                            <span className="text-xs text-slate-400 ml-2">
                              ({med.genericName})
                            </span>
                          )}
                        </div>
                      ))}
                    {medicines.length === 0 || medicineName.trim() === "" ? (
                      <div className="px-4 py-2 text-sm text-slate-500">
                        No medicines found
                      </div>
                    ) : (
                      <div className="px-4 py-2 text-sm text-slate-500">
                        No matching medicines
                      </div>
                    )}
                  </div>
                )}
              </>
            )}
            {fieldErrors.medicine && (
              <p className="mt-1 text-sm text-red-600">{fieldErrors.medicine}</p>
            )}
          </div>
        </div>

        {/* Duration */}
        <div>
          <label className="mb-1.5 block text-sm font-medium text-slate-700">
            Duration
          </label>
          <DurationPicker value={duration} onChange={setDuration} />
        </div>

        {/* Dosage Pattern */}
        <div>
          <label className="mb-1.5 block text-sm font-medium text-slate-700">
            Dosage Pattern
          </label>
          <DosageSelector
            morning={morning}
            afternoon={afternoon}
            night={night}
            onChange={handleDosageChange}
          />
          <div className="mt-2">
            <DosageExplanation morning={morning} afternoon={afternoon} night={night} />
          </div>
        </div>

        {/* Meal Timing */}
        <div>
          <label className="mb-1.5 block text-sm font-medium text-slate-700">
            Meal Timing
          </label>
          <MealTimingSelector value={mealTiming} onChange={setMealTiming} />
        </div>

        {/* Reminder Time */}
        <div>
          <label className="mb-1.5 block text-sm font-medium text-slate-700">
            Reminder Time
          </label>
          <ReminderPicker value={reminder} onChange={setReminder} />
        </div>

        {/* Notes */}
        <div>
          <label className="mb-1.5 block text-sm font-medium text-slate-700">
            Notes
          </label>
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Optional notes..."
            rows={3}
            className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 placeholder-slate-400 shadow-soft transition focus:border-brand-300 focus:outline-none focus:ring-4 focus:ring-brand-100"
          />
        </div>

        {/* Submit Error */}
        {submitError && (
          <div className="mb-4 p-3 bg-red-50 text-red-700 rounded">
            {submitError}
          </div>
        )}

        {/* Submit Button */}
        <button
          type="button"
          disabled={submitLoading}
          onClick={handleSubmit}
          className={`w-full rounded-2xl bg-brand-500 py-3.5 text-base font-semibold text-white shadow-lg shadow-brand-200 transition hover:bg-brand-600 disabled:opacity-50 ${
            submitLoading ? "pointer-events-none" : ""
          }`}
        >
          {submitLoading ? (
            <>
              <svg className="mr-2 h-4 w-4 animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"></path>
              </svg>
              Saving...
            </>
          ) : (
            "Save Schedule"
          )}
        </button>
      </div>
    </Card>
  );
}