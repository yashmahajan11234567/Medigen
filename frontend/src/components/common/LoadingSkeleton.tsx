interface LoadingSkeletonProps {
  width?: number | string;
  height?: number | string;
  className?: string;
}

export function LoadingSkeleton({
  width = "100%",
  height = "1rem",
  className = "",
}: LoadingSkeletonProps) {
  return (
    <div
      className={`
        bg-slate-200 rounded animate-pulse h-full w-full
        ${className}
      `}
      style={{ width, height }}
    />
  );
}