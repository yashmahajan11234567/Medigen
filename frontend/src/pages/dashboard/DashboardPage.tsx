import { DashboardHeader } from "@/pages/dashboard/components/DashboardHeader";
import { SearchBar } from "@/pages/dashboard/components/SearchBar";
import { QuickActionCard } from "@/pages/dashboard/components/QuickActionCard";
import { StatsCard } from "@/pages/dashboard/components/StatsCard";
import { TodaysMedicines } from "@/pages/dashboard/components/TodaysMedicines";
import { LowStockMedicines } from "@/pages/dashboard/components/LowStockMedicines";
import { RecentRecords } from "@/pages/dashboard/components/RecentRecords";
import { useDashboard } from "@/hooks/useDashboard";
import { PageError } from "@/components/feedback/PageError";
import { useToast } from "@/components/ui/ToastProvider";
import { Pill, Scan, Archive, QrCode, RefreshCw } from "lucide-react";
import { LoadingScreen } from "@/components/common/LoadingScreen";

export function DashboardPage() {
  const { dashboard, loading, error, refetch } = useDashboard();
  const { addToast } = useToast();

  if (loading && !dashboard) {
    return (
      <LoadingScreen
        title="Loading your dashboard..."
        description="Connecting the MediGen frontend to your account and settings."
      />
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center px-6">
        <PageError
          title="Something went wrong"
          description="We couldn't load your dashboard. Please try again."
          onRetry={() => {
            refetch();
            addToast({
              title: "Dashboard refreshed.",
              description: "We've refreshed your dashboard.",
              variant: "success",
            });
          }}
        />
      </div>
    );
  }

  // Extract data for convenience
  const user = dashboard?.user ?? { name: "" };
  const today_schedule = dashboard?.today_schedule ?? [];
  const inventory_summary = dashboard?.inventory_summary ?? { total_medicines: 0, expiring_soon: 0 };
  const medical_records_count = 0;
  const generic_searches_count = 0;
  const low_stock_list: any[] = [];
  const recent_records: any[] = [];

  // Stats data
  const stats = [
    {
      title: "Medicines in Inventory",
      value: inventory_summary.total_medicines,
      icon: "Pill", // We'll map to actual icon later
      accent: "blue",
    },
    {
      title: "Today's Medicines",
      value: today_schedule.length,
      icon: "Scan",
      accent: "green",
    },
    {
      title: "Medical Records",
      value: medical_records_count,
      icon: "Archive",
      accent: "purple",
    },
    {
      title: "Generic Searches",
      value: generic_searches_count,
      icon: "QrCode",
      accent: "amber",
    },
  ] as const;

  // Quick actions (static)
  const quickActions = [
    {
      title: "Scan Medicine",
      description: "OCR-powered medicine strip scanning",
      icon: "Scan",
      to: "/scan",
      accent: "blue",
    },
    {
      title: "Inventory",
      description: "Track your medicine stock",
      icon: "Pill",
      to: "/inventory",
      accent: "green",
    },
    {
      title: "Scheduler",
      description: "Set medicine reminders",
      icon: "QrCode",
      to: "/schedule",
      accent: "amber",
    },
    {
      title: "Medical Records",
      description: "Store health documents",
      icon: "Archive",
      to: "/medical-records",
      accent: "purple",
    },
  ] as const;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <DashboardHeader name={user.name} />
        <button
          onClick={async () => {
            await refetch();
            addToast({
              title: "Dashboard updated.",
              description: "Your dashboard has been refreshed.",
              variant: "success",
            });
          }}
          className="flex items-center justify-center w-10 h-10 rounded-full bg-brand-500 text-white hover:bg-brand-600 transition-colors duration-200"
          aria-label="Refresh dashboard"
        >
          <RefreshCw className="h-4 w-4" />
        </button>
      </div>

      <SearchBar />

      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {stats.map((stat) => {
          // Map icon string to actual icon component
          const iconMap: Record<string, typeof Pill> = {
            Pill,
            Scan,
            Archive,
            QrCode,
          };
          const Icon = iconMap[stat.icon] || Pill;
          return (
            <StatsCard
              key={stat.title}
              title={stat.title}
              value={stat.value}
              icon={Icon}
              accent={stat.accent}
            />
          );
        })}
      </div>

      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        {quickActions.map((action) => {
          const iconMap: Record<string, typeof Pill> = {
            Pill,
            Scan,
            Archive,
            QrCode,
          };
          const Icon = iconMap[action.icon] || Pill;
          return (
            <QuickActionCard
              key={action.title}
              title={action.title}
              description={action.description}
              icon={Icon}
              to={action.to}
              accent={action.accent}
            />
          );
        })}
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <TodaysMedicines todaySchedule={today_schedule} />
        <LowStockMedicines lowStockList={low_stock_list} />
      </div>

      <RecentRecords recentRecords={recent_records} />
    </div>
  );
}