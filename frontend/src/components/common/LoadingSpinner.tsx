import { Loader2 } from "lucide-react";

interface LoadingSpinnerProps {
  size?: number;
  className?: string;
}

export function LoadingSpinner({
  size = 24,
  className = "",
}: LoadingSpinnerProps) {
  return (
    <Loader2
      className={`
        h-${size} w-${size}
        animate-spin
        ${className}
      `}
    />
  );
}