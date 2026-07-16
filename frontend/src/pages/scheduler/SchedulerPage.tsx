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
  ScheduleUpdateRequest,
  ScheduleResponse,
} from "@/types/api";

export function SchedulerPage() {
  const {
    schedules,
    loading: schedulesLoading,
    error: schedulesError,
    createSchedule,
    updateSchedule,
    deleteSchedule,
    fetchSchedules,
    todaySchedule,
    loading: todayLoading,
    error: todayError,
    completeReminder,
    fetchTodaySchedule,
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

  const [editMode, setEditMode] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [formLoading, setFormLoading] = useState(false);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => {
    const target = e.target;
    const { name, type, value } = target;

    let val: any;
    if (type === "number") {
      const numValue = value;
      val = numValue === "" ? null : Number(numValue);
    } else {
      val = value;
    }

    setFormData((prev) => ({
      ...prev,
      [name]: val,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormLoading(true);
    try {
      if (editMode && editingId !== null) {
        await updateSchedule(editingId, formData as unknown as ScheduleUpdateRequest);
        // Reset form and hide
        setEditMode(false);
        setEditingId(null);
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
        await fetchSchedules(); // Refresh list
      } else {
        await createSchedule(formData);
        // Reset form
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
        await fetchSchedules(); // Refresh list
      }
    } catch (err: any) {
      // Error is shown via the hook's error state
    } finally {
      setFormLoading(false);
    }
  };

  const handleEdit = (schedule: ScheduleResponse) => {
    setEditMode(true);
    setEditingId(schedule.id);
    // Build reminder_times object from reminders array
    const reminderTimes: { morning: string | null; afternoon: string | null; night: string | null } = {
      morning: null,
      afternoon: null,
      night: null,
    };
    schedule.reminders?.forEach((reminder) => {
      if (reminder.period === "morning") {
        reminderTimes.morning = reminder.reminder_time;
      } else if (reminder.period === "afternoon") {
        reminderTimes.afternoon = reminder.reminder_time;
      } else if (reminder.period === "night") {
        reminderTimes.night = reminder.reminder_time;
      }
    });
    setFormData({
      medicine_id: schedule.medicine_id,
      dosage_pattern: schedule.dosage_pattern,
      food_tyming: schedule.food_timing,
      start_date: schedule.start_date,
      end_date: schedule.end_date,
      duration_days: schedule.duration_days,
      reminder_times: reminderTimes,
      notes: schedule.notes ?? null,
      quantity: schedule.quantity ?? null,
      quantity_unit: schedule.quantity_unit ?? null,
      purchase_date: schedule.purchase_date ?? null,
      expiry_date: schedule.expiry_date ?? null,
      pharmacy_name: schedule.pharmacy_name ?? null,
      source: schedule.source,
    });
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm("Are you sure you want to delete this schedule?")) {
      return;
    }
    try {
      await deleteSchedule(id);
      // The deleteSchedule hook updates the state, so we don't need to refetch.
      // But we'll refetch to be safe.
      await fetchSchedules();
    } catch (err: any) {
      alert("Failed to delete schedule: " + (err.response?.data?.message || err.message));
    }
  };

  const handleCompleteReminder = async (reminderId: number) => {
    try {
      await completeReminder(reminderId);
      // Refresh today's schedule after completion
      await fetchTodaySchedule();
      // Also refresh schedules in case completion affects status
      await fetchSchedules();
    } catch (err: any) {
      alert("Failed to complete reminder: " + (err.response?.data?.message || err.message));
    }
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
      {todayError && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-800">
          <InlineError title="Today's Schedule Error" message={todayError} />
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
              <div>
                <label className="block mb-1 font-medium text-slate-900">
                  Reminder Times
                </label>
                <div className="grid gap-2 sm:grid-cols-3">
                  <div>
                    <Input
                      label="Morning (HH:MM)"
                      name="morning"
                      type="text"
                      value={formData.reminder_times?.morning ?? ""}
                      onChange={handleChange}
                      className="mb-2"
                    />
                  </div>
                  <div>
                    <Input
                      label="Afternoon (HH:MM)"
                      name="afternoon"
                      type="text"
                      value={formData.reminder_times?.afternoon ?? ""}
                      onChange={handleChange}
                      className="mb-2"
                    />
                  </div>
                  <div>
                    <Input
                      label="Night (HH:MM)"
                      name="night"
                      type="text"
                      value={formData.reminder_times?.night ?? ""}
                      onChange={handleChange}
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
            </div>

            <Button type="submit" variant="primary" disabled={formLoading}>
              {formLoading ? "Saving..." : "Add Schedule"}
            </Button>
            <Button
              type="button"
              variant="secondary"
              size="sm"
              onClick={() => {
                setEditMode(false);
                setEditingId(null);
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
              }}
            >
              Cancel
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
                      <span>{schedule.status}</span>
                    </div>
                  </div>
                  <div className="mt-3 flex justify-end space-x-2">
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={() => handleEdit(schedule)}
                    >
                      Edit
                    </Button>
                    <Button
                      variant="danger"
                      size="sm"
                      onClick={() => handleDelete(schedule.id)}
                    >
                      Delete
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>

        <Card>
          <h2 className="mb-4 text-lg font-semibold text-slate-900">
            Today's Schedule ({todaySchedule.length})
          </h2>
          {todayLoading && todaySchedule.length === 0 ? (
            <LoadingScreen
              title="Loading today's schedule…"
              description="Please wait while we load today's schedule."
            />
          ) : todayError ? (
            <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-800">
              <InlineError title="Load error" message={todayError} />
            </div>
          ) : todaySchedule.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-sm text-slate-500">
                No medications scheduled for today.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {todaySchedule.map((schedule) => (
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
                      <p className="text-sm text-slice-600">
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
                      {schedule.reminders && schedule.reminders.length > 0 ? (
                        <div className="mt-3 space-y-2">
                          <p className="font-medium text-slate-700">
                            Reminders for today:
                          </p>
                          {schedule.reminders.map((reminder) => (
                            <div
                              key={reminder.id}
                              className="flex items-center justify-between p-2 bg-white/50 rounded"
                            >
                              <span>
                                {reminder.period}: {
                                  new Date(
                                    `1970-01-01T${reminder.reminder_time}:00Z`
                                  ).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
                                }
                              </span>
                              <Button
                                variant="secondary"
                                size="sm"
                                onClick={() => handleCompleteReminder(reminder.id)}
                                disabled={reminder.completed_at !== null}
                              >
                                {reminder.completed_at ? "Completed" : "Complete"}
                              </Button>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <p className="text-sm text-slate-500">
                          No reminders scheduled for today.
                        </p>
                      )}
                    </div>
                    <div className="text-xs text-slate-500">
                      <span>{schedule.status}</span>
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