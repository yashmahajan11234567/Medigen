import { AlertTriangle } from "lucide-react";
import { cn } from "@/lib/cn";

interface PageErrorProps {
  title: string;
  description?: string;
  className?: string;
  onRetry?: () => void;
}

export function PageError({
  title,
  description,
  className,
  onRetry,
}: PageErrorProps) {
  return (
    <div
      className={cn(
        "flex w-full flex-col items-center justify-center p-6 text-center",
        "border border-dashed rounded-lg",
        "bg-[color:rgb(254_242_242)]",
        className
      )}
    >
      <div className="mb-4">
        <AlertTriangle className="h-8 w-8 text-red-500" />
      </div>
      <h2 className="mb-2 text-lg font-semibold text-red-600">{title}</h2>
      {description && (
        <p className="mb-4 text-sm text-gray-600">{description}</p>
      )}
      {onRetry && (
        <button
          onClick={onRetry}
          className="btn btn-primary"
        >
          Retry
        </button>
      )}
    </div>
  );
}