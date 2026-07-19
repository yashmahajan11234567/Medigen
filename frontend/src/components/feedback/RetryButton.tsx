import { RefreshCw } from "lucide-react";

interface RetryButtonProps {
  onClick: () => void;
  children?: React.ReactNode;
  className?: string;
  disabled?: boolean;
  size?: "default" | "sm" | "lg";
}

export function RetryButton({
  onClick,
  children = "Retry",
  className = "",
  disabled = false,
  size = "default",
}: RetryButtonProps) {
  const sizeMap: Record<string, string> = {
    sm: "px-3 py-1.5 text-sm",
    default: "px-4 py-2 text-base",
    lg: "px-6 py-3 text-lg",
  };

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`
        flex items-center justify-center gap-2 rounded-md
        border border-transparent bg-primary py-2 px-4 text-sm font-medium
        text-primary-foreground hover:bg-primary/80
        transition-colors duration-200
        ${sizeMap[size]}
        ${disabled ? "opacity-50 cursor-not-allowed" : ""}
        ${className}
      `}
    >
      {children && (
        <>
          <RefreshCw className="h-4 w-4" />
          <span className="ml-2">{children}</span>
        </>
      )}
      {!children && (
        <>
          <RefreshCw className="h-4 w-4" />
          <span className="ml-2">Retry</span>
        </>
      )}
    </button>
  );
}