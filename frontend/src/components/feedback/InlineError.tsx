import { AlertCircle } from "lucide-react";
import { cn } from "@/lib/cn";

interface InlineErrorProps {
  title?: string;
  message: string;
  className?: string;
}

export function InlineError({
  title = "Something needs attention",
  message,
  className,
}: InlineErrorProps) {
  return (
    <div
      className={cn(
        "flex gap-3 rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700",
        className,
      )}
      role="alert"
    >
      <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
      <div>
        <p className="font-semibold">{title}</p>
        <p className="mt-1 leading-6">{message}</p>
      </div>
    </div>
  );
}
