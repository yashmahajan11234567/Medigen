import type { ReactNode } from "react";

interface SectionTitleProps {
  children: ReactNode;
}

export function SectionTitle({ children }: SectionTitleProps) {
  return (
    <div className="flex items-center gap-3">
      <div className="h-1 w-8 rounded-full bg-brand-500" />
      <h2 className="text-lg font-semibold text-slate-900">{children}</h2>
    </div>
  );
}