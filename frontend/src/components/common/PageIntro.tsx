import { Card } from "@/components/common/Card";

interface PageIntroProps {
  eyebrow: string;
  title: string;
  description: string;
}

export function PageIntro({ eyebrow, title, description }: PageIntroProps) {
  return (
    <Card className="overflow-hidden p-6 sm:p-8">
      <div className="flex flex-col gap-3">
        <span className="text-xs font-semibold uppercase tracking-[0.26em] text-mint-700">
          {eyebrow}
        </span>
        <h1 className="text-2xl font-semibold text-slate-900 sm:text-3xl">{title}</h1>
        <p className="max-w-2xl text-sm leading-7 text-slate-600 sm:text-base">
          {description}
        </p>
      </div>
    </Card>
  );
}
