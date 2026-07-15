import { useState } from "react";
import { PageIntro } from "@/components/common/PageIntro";
import { Input } from "@/components/common/Input";
import { Button } from "@/components/common/Button";
import { Card } from "@/components/common/Card";
import { EmptyState } from "@/components/common/EmptyState";
import { LoadingScreen } from "@/components/common/LoadingScreen";
import { InlineError } from "@/components/feedback/InlineError";
import { useScheduler } from "@/hooks/useScheduler";
import { Calendar } from "lucide-react";
import type {
  ScheduleCreateRequest,
  ScheduleResponse,
} from "@/types/api";

export function SchedulerPage() {
  const {
    schedules,
    loading: schedulesLoading,
    error: schedulesError,
    createSchedule,
    fetchSchedules,
  } = useScheduler();

  const [formData, setFormData] = useState<ScheduleCreateRequest>({
    medicine_id: 0,
    dosage_pattern: "",
    food_tyming: "before_food",
    start_date: new Date().toISOString().split("T")[0],
    end_date: null,
    duration_days: null,
    reminder_times: { morning: null, afternoon: null, night: null },
    notes: null,
    quantity: null,
    quantity_unit: null,
    purchase_date: null,
    expiry_date: null,
    pharmacy_name: null,
    source: "manual",
  });

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]:
        type === "checkbox"
          ? checked
          : type === "number"
          ? value === ""
            ? null
            : Number(value)
          : value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await createSchedule(formData);
    // reset form
    setFormData({
      medicine_id: 0,
      dosage_pattern: "",
      food_tyming: "before_food",
      start_date: new Date().toISOString().split("T")[0],
      end_date: null,
      duration_days: null,
      reminder_times: { morning: null, afternoon: null, night: null },
      notes: null,
      quantity: null,
      quantity_unit: null,
      purchase_date: null,
      expiry_date: null,
      pharmacy_name: null,
      source: "manual",
    });
    await fetchSchedules();
  };

  return (
    <>
      <PageIntro
        eyebrow="Scheduler"
        title="Medication Schedule"
        description="Manage your medication reminders and dosing schedule."
      />
      {schedulesError && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-800">
          <InlineError title="Error" message={schedulesError} />
        </div>
      )}
      <div className="space-y-6">
        <Card>
          <h2 className="mb-4 text-lg font-semibold text-slate-900">
            Add Schedule
          </h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <Input
                  label="Medicine ID"
                  name="medicine_id"
                  type="number"
                  value={formData.medicine_id ?? ""}
                  onChange={handleChange}
                  className="mb-2"
                />
              </div>
              <div>
                <Input
                  label="Dosage Pattern (e.g., 1-0-1)"
                  name="dosage_pattern"
                  type="text"
                  value={formData.dosage_pattern ?? ""}
                  onChange={handleChange}
                  className="mb-2"
                />
              </div>
              <div>
                <label className="block mb-1 font-medium text-slate-900">
                  Food Timing
                </label>
                <select
                  name="food_tyming"
                  value={formData.food_tyming}
                  onChange={handleChange}
                  className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                >
                  <option value="before_food">Before Food</option>
                  <option value="after_food">After Food</option>
                </select>
              </div>
              <div>
                <Input
                  label="Start Date (YYYY-MM-DD)"
                  name="start_date"
                  type="date"
                  value={formData.start_date ?? ""}
                  onChange={handleChange}
                  className="mb-2"
                />
              </div>
              <div>
                <Input
                  label="End Date (optional)"
                  name="end_date"
                  type="date"
                  value={formData.end_date ?? ""}
                  onChange={handleChange}
                  className="mb-2"
                />
              </div>
              <div>
                <Input
                  label="Duration Days (optional)"
                  name="duration_days"
                  type="number"
                  value={formData.duration_days ?? ""}
                  onChange={handleChange}
                  className="mb-2"
                />
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
                  label="Pharmacy Name (optional)"
                  name="pharmacy_name"
                  type="text"
                  value={formData.pharmacy_name ?? ""}
                  onChange={handleChange}
                  className="mb-2"
                />
              </div>
              <div>
                <label className="block mb-1 font-medium text-slate-900">
                  Source
                </label>
                <select
                  name="source"
                  value={formData.source}
                  onChange={handleChange}
                  className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                >
                  <option value="manual">Manual</option>
                  <option value="pharmacy_bill">Pharmacy Bill</option>
                  <option value="generic_finder">Generic Finder</option>
                </select>
              </div>
            </div>

            <div className="mt-4">
              <label className="block mb-1 font-medium text-slate-900">
                Reminder Times (optional)
              </label>
              <div className="grid gap-4 sm:grid-cols-3">
                <div>
                  <Input
                    label="Morning (HH:MM)"
                    type="text"
                    value={formData.reminder_times?.morning ?? ""}
                    onChange={(e) => {
                      const target = e.target as HTMLInputElement;
                      const value = target.value === "" ? null : target.value;
                      setFormData((prev) => ({
                        ...prev,
                        reminder_times: {
                          ...(prev.reminder_times || {}),
                          morning: value,
                        },
                      }));
                    }}
                    className="mb-2"
                  />
                </div>
                <div>
                  <Input
                    label="Afternoon (HH:MM)"
                    type="text"
                    value={formData.reminder_times?.afternoon ?? ""}
                    onChange={(e) => {
                      const target = e.target as HTMLInputElement;
                      const value = target.value === "" ? null : target.value;
                      setFormData((prev) => ({
                        ...prev,
                        reminder_times: {
                          ...(prev.reminder_times || {}),
                          afternoon: value,
                        },
                      }));
                    }}
                    className="mb-2"
                  />
                </div>
                <div>
                  <Input
                    label="Night (HH:MM)"
                    type="text"
                    value={formData.reminder_times?.night ?? ""}
                    onChange={(e) => {
                      const target = e.target as HTMLInputElement;
                      const value = target.value === "" ? null : target.value;
                      setFormData((prev) => ({
                        ...prev,
                        reminder_times: {
                          ...(prev.reminder_times || {}),
                          night: value,
                        },
                      }));
                    }}
                    className="mb-2"
                  />
                </div>
              </div>
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

            <Button type="submit" variant="primary" disabled={schedulesLoading}>
              {schedulesLoading ? "Adding..." : "Add Schedule"}
            </Button>
          </form>
        </Card>

        <Card>
          <h2 className="mb-4 text-lg font-semibold text-slate-900">
            Schedule List ({schedules.length})
          </h2>
          {schedulesLoading && schedules.length === 0 ? (
            <LoadingScreen
              title="Loading schedules…"
              description="Please wait while we load your schedules."
            />
          ) : schedulesError ? (
            <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-800">
              <InlineError title="Load error" message={schedulesError} />
            </div>
          ) : schedules.length === 0 ? (
            <EmptyState
              icon={Calendar}
              title="No schedules yet"
              description="Add your first schedule using the form above."
            />
          ) : (
            <div className="space-y-4">
              {schedules.map((schedule) => (
                <div
                  key={schedule.id}
                  className="p-4 bg-slate-50 border border-slate-200 rounded-lg"
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="font-medium text-slate-900">
                        Schedule #{schedule.id}
                      </h3>
                      <p className="text-sm text-slate-600">
                        Medicine ID: {schedule.medicine_id}
                      </p>
                      <p className="text-sm text-slate-600">
                        {schedule.dosage_pattern} • {schedule.food_timing}
                      </p>
                      {schedule.start_date && (
                        <p className="text-sm text-slate-600">
                          Starts:{" "}
                            {new Date(schedule.start_date).toLocaleDateString()}
                        </p>
                      )}
                      {schedule.end_date && (
                        <p className="text-sm text-slate-600">
                          Ends:{" "}
                            {new Date(schedule.end_date).toLocaleDateString()}
                        </p>
                      )}
                      {schedule.notes && (
                        <p className="text-sm text-slate-600 italic">
                          {schedule.notes}
                        </p>
                      )}
                    </div>
                    <div className="text-xs text-slate-500">
                      {schedule.status}
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