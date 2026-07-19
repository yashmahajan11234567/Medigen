import { cn } from "@/lib/cn";

interface DosageExplanationProps {
  morning: number;
  afternoon: number;
  night: number;
}

function getExplanation(morning: number, afternoon: number, night: number): string {
  const parts: string[] = [];
  if (morning === 1) parts.push("Morning");
  if (afternoon === 1) parts.push("Afternoon");
  if (night === 1) parts.push("Night");
  if (parts.length === 0) return "No doses selected";
  if (parts.length === 3) return "Morning, Afternoon & Night";
  return parts.join(" & ");
}

export function DosageExplanation({ morning, afternoon, night }: DosageExplanationProps) {
  const explanation = getExplanation(morning, afternoon, night);
  const hasDoses = morning === 1 || afternoon === 1 || night === 1;

  return (
    <p
      className={cn(
        "rounded-xl px-4 py-2.5 text-center text-sm font-medium",
        hasDoses ? "bg-mint-50 text-mint-700" : "bg-slate-50 text-slate-400",
      )}
    >
      {explanation}
    </p>
  );
}