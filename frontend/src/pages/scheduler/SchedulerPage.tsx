import { useState } from "react";
import { ScheduleForm } from "@/pages/scheduler/components/ScheduleForm";
import { ScheduleEditModal } from "@/pages/scheduler/components/ScheduleEditModal";
import { EmptySchedule } from "@/pages/scheduler/components/EmptySchedule";
import { ScheduleCard } from "@/pages/scheduler/components/ScheduleCard";
import { useScheduler } from "@/hooks/useScheduler";
import { useToast } from "@/components/ui/ToastProvider";
import { PageError } from "@/components/feedback/PageError";

export function SchedulerPage() {
  const {
    schedules,
    todaySchedules,
    loading,
    refreshing,
    error,
    success,
    refresh,
    createSchedule,
    updateSchedule,
  } = useScheduler();

  const [shownSuccess, setShownSuccess] = useState(false);
  const { addToast } = useToast();
  const [editSchedule, setEditSchedule] = useState<{
    schedule: typeof schedules[number];
  } | null>(null);

  // Format time from HH:MM:SS to h:mm A
  const formatTime = (timeStr: string | null): string => {
    if (!timeStr) return "";
    const [hours, minutes] = timeStr.split(":");
    const hoursNum = parseInt(hours, 10);
    const minutesNum = parseInt(minutes, 10);
    const period = hoursNum >= 12 ? "PM" : "AM";
    const hours12 = hoursNum % 12 === 0 ? 12 : hoursNum % 10;
    const minutesStr = minutesNum.toString().padStart(2, "0");
    return `${hours12}:${minutesStr} ${period}`;
  };

  // Transform a ScheduleResponse to ScheduleCardProps for today's display
  const transformToCardProps = (schedule: any): any => {
    // Format dosage: "1-0-1" -> "[1] - [0] - [1]"
    const dosageParts = schedule.dosage_pattern.split("-");
    const dosageFormatted = dosageParts
      .map((part: string) => `[${part}]`)
      .join(" - ");

    // Format meal timing: "after_food" -> "After Meal"
    const mealTimingFormatted = schedule.food_timing
      .split("_")
      .map((word: string) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ")
      .replace("Food", "Meal");

    // Get the first reminder time
    const firstReminder = schedule.reminders?.[0];
    const reminderTime = formatTime(firstReminder?.reminder_time ?? null);

    // Determine status based on the first reminder's completion status
    let status: "upcoming" | "taken" | "missed" = "upcoming";
    if (firstReminder) {
      if (firstReminder.completed_at !== null) {
        status = "taken";
      } else {
        // We don't have enough info to determine if it's missed, so we assume upcoming
        status = "upcoming";
      }
    }

    return {
      name: schedule.medicine_name,
      dosage: dosageFormatted,
      mealTiming: mealTimingFormatted,
      reminder: reminderTime,
      status,
    };
  };

  // Compute stats for today's schedule
  const computedToday = todaySchedules.map((s: any) => ({
    ...s,
    ...transformToCardProps(s),
  }));
  const totalToday = computedToday.length;
  const completedToday = computedToday.filter(
    (c: any) => c.status === "taken"
  ).length;
  const remainingToday = totalToday - completedToday;

  const stats = [
    { label: "Medicines Today", value: totalToday, accent: "bg-brand-500" },
    { label: "Taken", value: completedToday, accent: "bg-mint-500" },
    { label: "Remaining", value: remainingToday, accent: "bg-amber-500" },
  ];

  // Show toast when success is set and we haven't shown it yet
  if (success && !shownSuccess) {
    addToast({
      title: "Schedule updated.",
      description: success,
      variant: "success",
    });
    setShownSuccess(true);
  }

  // Reset shownSuccess when success is cleared
  if (!success && shownSuccess) {
    setShownSuccess(false);
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center px-6">
        <div className="w-full max-w-md">
          <PageError title="Error" description={error} onRetry={refresh} />
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center px-6">
        <div className="text-center">
          <h1 className="text-2xl font-semibold text-slate-900 mb-4">
            Loading your schedule...
          </h1>
          <p className="mb-4">
            Fetching your medicine schedule from the server.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Custom header with schedule button */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-4">
          <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-brand-100 text-brand-600">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-6 w-6"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={1.5}
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div>
            <h1 className="text-xl font-semibold text-slate-900">Medicine Scheduler</h1>
            <p className="mt-0.5 text-sm text-slate-500">
              Never miss your medicines.
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => {
              // We'll just focus on the form or open a modal for creating a schedule.
              // For now, we'll do nothing because the form is always visible.
              // Alternatively, we could open a modal for creating a schedule.
              // We'll keep it simple and leave the form visible.
            }}
            className="flex h-10 w-10 items-center justify-center rounded-xl border border-slate-200 bg-white hover:bg-slate-50 transition-colors"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="mr-2 h-4 w-4"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={1.5}
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
            </svg>
          </button>
          <button
            type="button"
            disabled={refreshing}
            onClick={refresh}
            className={`flex h-10 w-10 items-center justify-center rounded-xl border border-slate-200 bg-white hover:bg-slate-50 transition-colors disabled:opacity-50 ${
              refreshing ? "animate-spin" : ""
            }`}
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className={`mr-2 h-4 w-4 ${refreshing ? "animate-spin" : ""}`}
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={1.5}
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 10h16M4 14h16" />
            </svg>
          </button>
        </div>
      </div>

      {/* Summary cards */}
      <div className="grid grid-cols-3 gap-3">
        {stats.map((stat, index) => (
          <div
            key={index}
            className={`p-4 text-center ${
              refreshing ? "opacity-50" : ""
            }`}
          >
            <div className="flex flex-col items-center">
              <p className="text-xs font-medium text-slate-500">{stat.label}</p>
              <div className="mt-2 flex h-9 w-24 items-center justify-center rounded-lg bg-slate-200">
                {refreshing ? (
                  <div className="w-full h-full" />
                ) : (
                  <span className="text-2xl font-bold text-slate-900">{stat.value}</span>
                )}
              </div>
              <div className="mt-2 h-2 w-24 rounded-full bg-slate-200">
                {refreshing ? (
                  <div className="w-full h-full" />
                ) : null}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Today's schedule list */}
      <div className="space-y-4">
        <div className="flex items-center gap-3">
          <div className="h-1 w-8 rounded-full bg-brand-500" />
          <h2 className="text-lg font-semibold text-slate-900">
            Today's Scheduled Medicines
          </h2>
        </div>
        {todaySchedules.length === 0 ? (
          <EmptySchedule />
        ) : (
          <div className="space-y-3">
            {todaySchedules.map((schedule) => {
              const cardProps = transformToCardProps(schedule);
              return (
                <div
                  key={schedule.id}
                  className={`opacity-${refreshing ? 50 : 100} transition-opacity`}
                >
                  <ScheduleCard
                    name={cardProps.name}
                    dosage={cardProps.dosage}
                    mealTiming={cardProps.mealTiming}
                    reminder={cardProps.reminder}
                    status={cardProps.status}
                    onClick={() => {
                      setEditSchedule({
                        schedule,
                      });
                    }}
                  />
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Schedule Form (for creating new schedules) */}
      <ScheduleForm onCreate={async (payload) => {
        try {
          await createSchedule(payload);
          // After successful creation, we refresh the data
          await refresh();
        } catch (err) {
          // Error is handled in the createSchedule function (which sets error state)
          // We don't need to do anything here.
        }
      }} />

      {/* Edit Schedule Modal */}
      {editSchedule && (
        <ScheduleEditModal
          open={true}
          onClose={() => setEditSchedule(null)}
          schedule={editSchedule.schedule}
          updateSchedule={async (id, payload) => {
            try {
              await updateSchedule(id, payload);
              // After successful update, we refresh the data
              await refresh();
              // Close the modal
              setEditSchedule(null);
            } catch (err) {
              // Error is handled in the updateSchedule function (which sets error state)
              // We don't need to do anything here.
            }
          }}
        />
      )}
    </div>
  );
}