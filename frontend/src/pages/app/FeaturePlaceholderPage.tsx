import { ArrowRight, Construction } from "lucide-react";
import { Link } from "react-router-dom";
import { Card } from "@/components/common/Card";
import { PageIntro } from "@/components/common/PageIntro";

interface FeaturePlaceholderPageProps {
  title: string;
  eyebrow: string;
  description: string;
  apiHighlights: string[];
}

export function FeaturePlaceholderPage({
  title,
  eyebrow,
  description,
  apiHighlights,
}: FeaturePlaceholderPageProps) {
  return (
    <div className="space-y-6">
      <PageIntro eyebrow={eyebrow} title={title} description={description} />

      <div className="grid gap-6 xl:grid-cols-[1.6fr_1fr]">
        <Card className="p-6 sm:p-8">
          <div className="flex items-start gap-4">
            <div className="flex h-14 w-14 items-center justify-center rounded-3xl bg-brand-50 text-brand-600">
              <Construction className="h-6 w-6" />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-slate-900">
                This route is intentionally a foundation placeholder
              </h2>
              <p className="mt-3 max-w-2xl text-sm leading-7 text-slate-600">
                The app shell, auth flow, route protection, and visual system are ready.
                The actual page implementation is deferred to later frontend phases so the
                UI can be built on top of a stable backend contract.
              </p>
            </div>
          </div>

          <div className="mt-8 grid gap-3 rounded-3xl bg-slate-50 p-5">
            <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-500">
              Backend APIs already available
            </p>
            {apiHighlights.map((item) => (
              <div
                key={item}
                className="rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-700"
              >
                {item}
              </div>
            ))}
          </div>
        </Card>

        <Card className="p-6">
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-mint-700">
            Next Approved Step
          </p>
          <h2 className="mt-3 text-xl font-semibold text-slate-900">
            Plug the finalized UI into this shell
          </h2>
          <p className="mt-3 text-sm leading-7 text-slate-600">
            Sidebar navigation, top-level layout, auth, routing, loading states, and error
            boundaries are already ready for the real feature components.
          </p>
          <Link
            to="/dashboard"
            className="mt-6 inline-flex items-center gap-2 text-sm font-semibold text-brand-700 hover:text-brand-800"
          >
            <span>Return to foundation overview</span>
            <ArrowRight className="h-4 w-4" />
          </Link>
        </Card>
      </div>
    </div>
  );
}
