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
import type { ScheduleResponse, ScheduleUpdateRequest, ReminderTimesInput } from "@/types/api";

interface ScheduleEditModalProps {
  open: boolean;
  onClose: () => void;
  schedule: ScheduleResponse;
  updateSchedule: (id: number, payload: ScheduleUpdateRequest) => Promise<any>;
}

export function ScheduleEditModal({ open, onClose, schedule, updateSchedule }: ScheduleEditModalProps) {
  const [medicineName, setMedicineName] = useState(schedule.medicine_name || "");
  const [duration, setDuration] = useState(
    schedule.duration_days ? `${schedule.duration_days} Days` : "7 Days"
  );
  const [morning, setMorning] = useState(
    schedule.dosage_pattern.split("-")[0] === "1" ? 1 : 0
  );
  const [afternoon, setAfternoon] = useState(
    schedule.dosage_pattern.split("-")[1] === "1" ? 1 : 0
  );
  const [night, setNight] = useState(
    schedule.dosage_pattern.split("-")[2] === "1" ? 1 : 0
  );
  // Initialize mealTiming from schedule.food_timing (e.g., "after_food" -> "After Meal")
  const [mealTiming, setMealTiming] = useState(
    schedule.food_timing
      ? schedule.food_timing
          .split("_")
          .map((w: string) => w[0].toUpperCase() + w.slice(1))
          .join(" ")
          .replace("Food", "Meal")
      : "After Meal"
  );
  // Initialize reminder from the first reminder's reminder_time
  const [reminder, setReminder] = useState(
    schedule.reminders?.[0]?.reminder_time ?? "08:00"
  );
  const [notes, setNotes] = useState(schedule.notes || "");
  const [medicines, setMedicines] = useState<MedicineItem[]>([]);
  const [selectedMedicineId, setSelectedMedicineId] = useState<number | null>(
    schedule.medicine_id ?? null
  );
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
    const durationMatch = duration.match(/^(\d+)\s*Days$/i);
    const durationDays = durationMatch ? parseInt(durationMatch[1], 10) : 7;

    // Convert mealTiming (e.g., "After Meal") to food_tyming (e.g., "after_food")
    const foodTymingValue = mealTiming
      .toLowerCase()
      .replace("meal", "food")
      .replace(" ", "_");

    // Prepare payload
    const payload: ScheduleUpdateRequest = {
      dosage_pattern: `${morning}-${afternoon}-${night}`,
      food_tyming: foodTymingValue,
      start_date: schedule.start_date, // Keep original start date
      end_date: schedule.end_date,
      duration_days: durationDays,
      reminder_times: {
        morning: reminder,
        afternoon: null,
        night: null,
      } as ReminderTimesInput,
      notes: notes || null,
      quantity: schedule.quantity,
      quantity_unit: schedule.quantity_unit,
      purchase_date: schedule.purchase_date,
      expiry_date: schedule.expiry_date,
      pharmacy_name: schedule.pharmacy_name,
      status: schedule.status,
    };

    setSubmitLoading(true);
    try {
      await updateSchedule(schedule.id, payload);
      onClose();
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
            "Failed to update schedule"
        );
      }
    } finally {
      setSubmitLoading(false);
    }
  };

  if (!open) return null;

  return (
    <>
      <div className="fixed inset-0 z-50 bg-black/30 backdrop-blur-sm" onClick={onClose} />
      <div className="fixed inset-x-4 top-1/2 z-50 -translate-y-1/2 sm:inset-x-auto sm:left-1/2 sm:w-full sm:max-w-md sm:-translate-x-1/2">
        <Card className="p-6">
          <SectionTitle>Edit Schedule</SectionTitle>
          <div className="mb-4">
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => setMedicineName("")}
                className={`
                  flex-1 items-center justify-between rounded-2xl px-4 py-2 text-sm font-medium transition
                  ${medicineName.trim() === "" ? "bg-brand-500 text-white" : "bg-slate-50 text-slate-600 hover:bg-slate-100"}
                `}
              >
                Search Medicine
              </button>
              <button
                type="button"
                onClick={() => {
                  // We don't have a manual entry button because we are already in manual entry
                  // This is just to match the original form's structure
                }}
                className={`
                  flex-1 items-center justify-between rounded-2xl px-4 py-2 text-sm font-medium transition
                  ${medicineName.trim() !== "" ? "bg-brand-500 text-white" : "bg-slate-50 text-slate-600 hover:bg-slate-100"}
                `}
              >
                Manual Entry
              </button>
            </div>
          </div>

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
                            medicineName.trim() === "" ||
                            m.name
                              .toLowerCase()
                              .includes(medicineName.toLowerCase())
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
                Updating...
              </>
            ) : (
              "Update Schedule"
            )}
          </button>
        </Card>
      </div>
    </>
  );
}