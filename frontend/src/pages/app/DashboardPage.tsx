import type { ComponentType, CSSProperties } from "react";
import {
  Bell,
  CheckCircle2,
  Clock3,
  Inbox,
  Pill,
  RefreshCcw,
  TriangleAlert,
} from "lucide-react";
import { Button } from "@/components/common/Button";
import { Card } from "@/components/common/Card";
import { EmptyState } from "@/components/common/EmptyState";
import { PageIntro } from "@/components/common/PageIntro";
import { InlineError } from "@/components/feedback/InlineError";
import { useDashboard } from "@/hooks/useDashboard";
import type { DashboardScheduleItem } from "@/types/api";

interface DashboardMetricCardProps {
  title: string;
  value: string;
  description: string;
  icon: ComponentType<{ className?: string }>;
  accentClassName: string;
}

function formatFirstName(name: string) {
  return name.trim().split(/\s+/)[0] ?? name;
}

function formatReminderTime(value: string | null) {
  if (!value) {
    return "Time not set";
  }

  const [hours = "0", minutes = "0"] = value.split(":");
  const date = new Date();
  date.setHours(Number(hours), Number(minutes), 0, 0);

  return new Intl.DateTimeFormat(undefined, {
    hour: "numeric",
    minute: "2-digit",
  }).format(date);
}

function formatFrequency(value: string | null) {
  if (!value) {
    return "Frequency not provided";
  }

  return value
    .toLowerCase()
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function formatDosage(item: DashboardScheduleItem) {
  const dosageParts = [item.dosage_amount, item.dosage_unit].filter(Boolean);
  return dosageParts.length > 0 ? dosageParts.join(" ") : "Dosage not provided";
}

function DashboardMetricCard({
  title,
  value,
  description,
  icon: Icon,
  accentClassName,
}: DashboardMetricCardProps) {
  return (
    <Card className="p-5 sm:p-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm font-medium text-slate-500">{title}</p>
          <p className="mt-3 text-3xl font-semibold tracking-tight text-slate-900">{value}</p>
          <p className="mt-2 text-sm leading-6 text-slate-600">{description}</p>
        </div>
        <div
          className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl ${accentClassName}`}
        >
          <Icon className="h-5 w-5" />
        </div>
      </div>
    </Card>
  );
}

function DashboardLoadingState() {
  return (
    <div className="space-y-6 animate-pulse">
      <Card className="p-6 sm:p-8">
        <div className="h-3 w-24 rounded-full bg-slate-200" />
        <div className="mt-4 h-10 w-64 rounded-2xl bg-slate-200" />
        <div className="mt-3 h-4 w-full max-w-2xl rounded-full bg-slate-100" />
        <div className="mt-2 h-4 w-full max-w-xl rounded-full bg-slate-100" />
      </Card>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {Array.from({ length: 4 }).map((_, index) => (
          <Card key={index} className="p-5 sm:p-6">
            <div className="h-4 w-24 rounded-full bg-slate-100" />
            <div className="mt-4 h-10 w-20 rounded-2xl bg-slate-200" />
            <div className="mt-3 h-4 w-full rounded-full bg-slate-100" />
          </Card>
        ))}
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.45fr_1fr]">
        <Card className="p-6">
          <div className="h-6 w-48 rounded-full bg-slate-200" />
          <div className="mt-6 space-y-4">
            {Array.from({ length: 3 }).map((_, index) => (
              <div key={index} className="rounded-3xl border border-slate-100 p-5">
                <div className="h-4 w-32 rounded-full bg-slate-200" />
                <div className="mt-3 h-4 w-full rounded-full bg-slate-100" />
                <div className="mt-2 h-4 w-40 rounded-full bg-slate-100" />
              </div>
            ))}
          </div>
        </Card>

        <Card className="p-6">
          <div className="h-6 w-40 rounded-full bg-slate-200" />
          <div className="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-1">
            <div className="h-28 rounded-3xl bg-slate-100" />
            <div className="h-28 rounded-3xl bg-slate-100" />
          </div>
          <div className="mt-6 h-3 rounded-full bg-slate-100" />
        </Card>
      </div>
    </div>
  );
}

function ScheduleCard({ schedule }: { schedule: DashboardScheduleItem[] }) {
  return (
    <Card className="p-6 sm:p-7">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-mint-700">
            Today's medicine schedule
          </p>
          <h2 className="mt-3 text-2xl font-semibold text-slate-900">
            Keep track of what is due today
          </h2>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-600">
            This is a read-only view from the existing dashboard API. Medicines are shown
            in the backend-provided schedule order for today.
          </p>
        </div>
        <div className="inline-flex items-center gap-2 rounded-full bg-brand-50 px-3 py-2 text-sm font-semibold text-brand-700">
          <Clock3 className="h-4 w-4" />
          <span>{schedule.length} due today</span>
        </div>
      </div>

      {schedule.length === 0 ? (
        <div className="mt-8 rounded-[1.75rem] border border-dashed border-slate-200 px-6 py-10">
          <EmptyState
            icon={CheckCircle2}
            title="No medicines scheduled for today"
            description="Your dashboard is clear for the day. When schedules are available, they will appear here automatically."
          />
        </div>
      ) : (
        <div className="mt-8 space-y-4">
          {schedule.map((item) => (
            <div
              key={item.id}
              className="rounded-[1.75rem] border border-slate-200 bg-slate-50/80 p-5"
            >
              <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
                <div className="flex items-start gap-4">
                  <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-brand-50 text-brand-600">
                    <Pill className="h-5 w-5" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-slate-900">
                      {item.medicine_name}
                    </h3>
                    <div className="mt-2 flex flex-wrap gap-2 text-sm text-slate-600">
                      <span className="rounded-full bg-white px-3 py-1 font-medium text-slate-700">
                        {formatDosage(item)}
                      </span>
                      <span className="rounded-full bg-white px-3 py-1">
                        {formatFrequency(item.frequency)}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="inline-flex items-center gap-2 self-start rounded-full bg-white px-3 py-2 text-sm font-semibold text-brand-700 shadow-sm">
                  <Clock3 className="h-4 w-4" />
                  <span>{formatReminderTime(item.reminder_time)}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
}

function InventorySummaryCard({
  totalMedicines,
  expiringSoon,
}: {
  totalMedicines: number;
  expiringSoon: number;
}) {
  if (totalMedicines === 0) {
    return (
      <Card className="p-6 sm:p-7">
        <p className="text-xs font-semibold uppercase tracking-[0.24em] text-brand-700">
          Inventory summary
        </p>
        <h2 className="mt-3 text-2xl font-semibold text-slate-900">
          No medicines in inventory yet
        </h2>
        <div className="mt-8 rounded-[1.75rem] border border-dashed border-slate-200 px-6 py-10">
          <EmptyState
            icon={Inbox}
            title="Inventory is currently empty"
            description="Once medicines enter your inventory, this dashboard will summarize stock volume and highlight items expiring soon."
          />
        </div>
      </Card>
    );
  }

  const healthyCount = Math.max(totalMedicines - expiringSoon, 0);
  const healthyWidth = `${(healthyCount / totalMedicines) * 100}%`;
  const expiringWidth = `${(expiringSoon / totalMedicines) * 100}%`;
  const expiringBannerClassName =
    expiringSoon > 0
      ? "border-amber-200 bg-amber-50 text-amber-800"
      : "border-mint-200 bg-mint-50 text-mint-800";
  const progressSegments: Array<{ className: string; style: CSSProperties }> = [];

  if (healthyCount > 0) {
    progressSegments.push({
      className: "h-full rounded-full bg-mint-500",
      style: { width: healthyWidth },
    });
  }

  if (expiringSoon > 0) {
    progressSegments.push({
      className: "h-full rounded-full bg-amber-400",
      style: { width: expiringWidth },
    });
  }

  return (
    <Card className="p-6 sm:p-7">
      <p className="text-xs font-semibold uppercase tracking-[0.24em] text-brand-700">
        Inventory summary
      </p>
      <h2 className="mt-3 text-2xl font-semibold text-slate-900">
        Your medicine stock at a glance
      </h2>
      <p className="mt-2 text-sm leading-6 text-slate-600">
        This panel stays read-only and reflects the counts already calculated by the
        inventory backend.
      </p>

      <div className="mt-8 grid gap-4 sm:grid-cols-2 xl:grid-cols-1">
        <div className="rounded-[1.75rem] bg-brand-50 p-5">
          <p className="text-sm font-medium text-brand-700">Total medicines</p>
          <p className="mt-3 text-3xl font-semibold text-slate-900">{totalMedicines}</p>
          <p className="mt-2 text-sm leading-6 text-slate-600">
            Medicines currently tracked in your inventory.
          </p>
        </div>

        <div className="rounded-[1.75rem] bg-amber-50 p-5">
          <p className="text-sm font-medium text-amber-700">Expiring soon</p>
          <p className="mt-3 text-3xl font-semibold text-slate-900">{expiringSoon}</p>
          <p className="mt-2 text-sm leading-6 text-slate-600">
            Medicines that need attention soon based on the backend summary.
          </p>
        </div>
      </div>

      <div className="mt-8">
        <div className="flex items-center justify-between text-xs font-semibold uppercase tracking-[0.22em] text-slate-500">
          <span>Inventory health</span>
          <span>{healthyCount} stable</span>
        </div>
        <div className="mt-3 flex h-3 overflow-hidden rounded-full bg-slate-100">
          {progressSegments.map((segment, index) => (
            <div key={index} className={segment.className} style={segment.style} />
          ))}
        </div>
      </div>

      <div className={`mt-6 rounded-3xl border px-4 py-4 text-sm ${expiringBannerClassName}`}>
        {expiringSoon > 0
          ? `${expiringSoon} medicine${expiringSoon === 1 ? "" : "s"} are expiring soon. Use the inventory module for follow-up action when needed.`
          : "No medicines are currently marked as expiring soon."}
      </div>
    </Card>
  );
}

export function DashboardPage() {
  const { dashboard, error, loading, refetch } = useDashboard();

  if (loading && !dashboard) {
    return <DashboardLoadingState />;
  }

  const firstName = dashboard ? formatFirstName(dashboard.user.name) : "there";
  const title = dashboard ? `${dashboard.greeting}, ${firstName}` : "Home Dashboard";
  const scheduleCount = dashboard?.today_schedule.length ?? 0;
  const totalMedicines = dashboard?.inventory_summary.total_medicines ?? 0;
  const expiringSoon = dashboard?.inventory_summary.expiring_soon ?? 0;
  const notificationCount = dashboard?.notification_count ?? 0;

  return (
    <div className="space-y-6">
      <PageIntro
        eyebrow="Page 1"
        title={title}
        description="Your home dashboard is read-only and brings together greeting, unread notifications, today's medicines, and inventory health using the single existing backend dashboard API."
      />

      {error ? (
        <Card className="p-5 sm:p-6">
          <InlineError
            title="Dashboard unavailable"
            message={error}
          />
          <div className="mt-4">
            <Button
              variant="secondary"
              icon={<RefreshCcw className="h-4 w-4" />}
              onClick={refetch}
            >
              Retry loading dashboard
            </Button>
          </div>
        </Card>
      ) : null}

      {dashboard ? (
        <>
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <DashboardMetricCard
              title="Unread notifications"
              value={String(notificationCount)}
              description={
                notificationCount === 0
                  ? "You're all caught up right now."
                  : `${notificationCount} notification${notificationCount === 1 ? "" : "s"} still need your attention.`
              }
              icon={Bell}
              accentClassName="bg-brand-50 text-brand-600"
            />
            <DashboardMetricCard
              title="Today's medicines"
              value={String(scheduleCount)}
              description={
                scheduleCount === 0
                  ? "No medicines are scheduled for today."
                  : `${scheduleCount} medicine reminder${scheduleCount === 1 ? "" : "s"} are due today.`
              }
              icon={Clock3}
              accentClassName="bg-mint-50 text-mint-700"
            />
            <DashboardMetricCard
              title="Inventory summary"
              value={String(totalMedicines)}
              description="Medicines currently tracked in your inventory."
              icon={Pill}
              accentClassName="bg-brand-50 text-brand-600"
            />
            <DashboardMetricCard
              title="Expiring soon"
              value={String(expiringSoon)}
              description={
                expiringSoon === 0
                  ? "No medicines are currently expiring soon."
                  : `${expiringSoon} medicine${expiringSoon === 1 ? "" : "s"} need attention soon.`
              }
              icon={TriangleAlert}
              accentClassName="bg-amber-50 text-amber-700"
            />
          </div>

          <div className="grid gap-6 xl:grid-cols-[1.45fr_1fr]">
            <ScheduleCard schedule={dashboard.today_schedule} />
            <InventorySummaryCard
              totalMedicines={totalMedicines}
              expiringSoon={expiringSoon}
            />
          </div>
        </>
      ) : null}
    </div>
  );
}
