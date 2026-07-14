import { HeartPulse } from "lucide-react";
import { Card } from "@/components/common/Card";
import { appConfig } from "@/lib/app-config";

interface LoadingScreenProps {
  title?: string;
  description?: string;
}

export function LoadingScreen({
  title = "Preparing your workspace",
  description = "Connecting the MediGen frontend to your account and settings.",
}: LoadingScreenProps) {
  return (
    <div className="flex min-h-screen items-center justify-center px-6">
      <Card className="w-full max-w-md p-8 text-center">
        <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-3xl bg-brand-50 text-brand-600">
          <HeartPulse className="h-8 w-8 animate-pulse" />
        </div>
        <p className="text-sm font-semibold uppercase tracking-[0.22em] text-brand-600">
          {appConfig.appName}
        </p>
        <h1 className="mt-3 text-2xl font-semibold text-slate-900">{title}</h1>
        <p className="mt-2 text-sm leading-6 text-slate-600">{description}</p>
        <div className="mt-6 h-2 overflow-hidden rounded-full bg-slate-100">
          <div className="h-full w-1/2 animate-pulse rounded-full bg-gradient-to-r from-brand-500 to-mint-500" />
        </div>
      </Card>
    </div>
  );
}
