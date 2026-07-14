import { Home, MapPinned } from "lucide-react";
import { Link } from "react-router-dom";
import { Card } from "@/components/common/Card";

export function NotFoundPage() {
  return (
    <div className="flex min-h-screen items-center justify-center px-6 py-10">
      <Card className="w-full max-w-xl p-8 text-center">
        <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-3xl bg-mint-50 text-mint-700">
          <MapPinned className="h-8 w-8" />
        </div>
        <p className="mt-6 text-xs font-semibold uppercase tracking-[0.26em] text-mint-700">
          404
        </p>
        <h1 className="mt-3 text-3xl font-semibold text-slate-900">
          That route is not part of the current frontend foundation
        </h1>
        <p className="mt-3 text-sm leading-7 text-slate-600">
          The shell, auth flow, and protected navigation are ready, but this path does not
          exist in the current phase.
        </p>
        <div className="mt-8 flex justify-center">
          <Link
            to="/dashboard"
            className="inline-flex items-center gap-2 rounded-2xl bg-brand-600 px-5 py-3 text-sm font-semibold text-white shadow-soft transition hover:bg-brand-700"
          >
            <Home className="h-4 w-4" />
            <span>Go to the protected shell</span>
          </Link>
        </div>
      </Card>
    </div>
  );
}
