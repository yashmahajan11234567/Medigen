import { Clock3, Pill } from "lucide-react";
import { Card } from "@/components/common/Card";
import { SectionTitle } from "@/pages/dashboard/components/SectionTitle";

interface MedicineItem {
  name: string;
  time: string;
  status: "upcoming" | "taken" | "missed";
}

interface BackendScheduleItem {
  id: number;
  medicine_id: number;
  medicine_name: string;
  dosage_amount: string | null;
  dosage_unit: string | null;
  frequency: string | null;
  reminder_time: string | null;
}

const statusConfig = {
  taken: { label: "Taken", dot: "bg-mint-500", bg: "bg-mint-50" },
  upcoming: { label: "Upcoming", dot: "bg-brand-500", bg: "bg-brand-50" },
  missed: { label: "Missed", dot: "bg-rose-500", bg: "bg-rose-50" },
};

export function TodaysMedicines({ todaySchedule }: { todaySchedule: BackendScheduleItem[] }) {
  // Convert backend schedule items to MedicineItem for UI
  const processedSchedule: MedicineItem[] = todaySchedule.map((item) => {
    // Default status to upcoming
    let status: "upcoming" | "taken" | "missed" = "upcoming";
    if (item.reminder_time) {
      const now = new Date();
      const reminderTime = new Date(item.reminder_time);
      if (reminderTime < now) {
        status = "taken";
      } else {
        status = "upcoming";
      }
    }
    // Format time from reminder_time (if available) else show "Time not set"
    const timeString = item.reminder_time
      ? new Date(item.reminder_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      : "Time not set";
    // Build medicine name with dosage if available
    const medicineName = item.medicine_name;
    const dosage = item.dosage_amount && item.dosage_unit
      ? `${item.dosage_amount} ${item.dosage_unit}`
      : "";
    const name = dosage ? `${medicineName} ${dosage}` : medicineName;
    return {
      name,
      time: timeString,
      status,
    };
  });

  return (
    <Card className="p-5 sm:p-6">
      <div className="flex items-center justify-between">
        <SectionTitle>Today's Medicines</SectionTitle>
        <div className="flex items-center gap-2 rounded-full bg-brand-50 px-3 py-1.5 text-sm font-semibold text-brand-700">
          <Clock3 className="h-4 w-4" />
          <span>{processedSchedule.length} today</span>
        </div>
      </div>

      <div className="mt-5 space-y-3">
        {processedSchedule.map((item) => {
          const s = statusConfig[item.status];
          return (
            <div
              key={item.name}
              className="flex items-center gap-4 rounded-2xl border border-slate-100 bg-white p-4 transition hover:shadow-sm"
            >
              <div className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl ${s.bg}`}>
                <Pill className={`h-5 w-5 ${s.dot.replace("bg-", "text-").replace("-500", "-600")}`} />
              </div>
              <div className="min-w-0 flex-1">
                <p className="font-semibold text-slate-900">{item.name}</p>
                <p className="mt-0.5 text-sm text-slate-500">{item.time}</p>
              </div>
              <div className="flex items-center gap-2 rounded-full bg-slate-50 px-3 py-1.5">
                <span className={`h-2 w-2 rounded-full ${s.dot}`} />
                <span className="text-xs font-semibold text-slate-600">{s.label}</span>
              </div>
            </div>
          );
        })}
      </div>
    </Card>
  );
}