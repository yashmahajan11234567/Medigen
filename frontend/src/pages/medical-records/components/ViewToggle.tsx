import { cn } from "@/lib/cn";
import { LayoutGrid, List } from "lucide-react";

interface ViewToggleProps {
  view: "gallery" | "list";
  onChange: (view: "gallery" | "list") => void;
}

export function ViewToggle({ view, onChange }: ViewToggleProps) {
  return (
    <div className="flex items-center gap-1 rounded-2xl bg-slate-100 p-1">
      <button
        type="button"
        onClick={() => onChange("gallery")}
        className={cn(
          "flex items-center gap-2 rounded-xl px-4 py-2 text-sm font-medium transition",
          view === "gallery"
            ? "bg-white text-brand-700 shadow-sm"
            : "text-slate-500 hover:text-slate-700",
        )}
        aria-label="Gallery view"
        aria-pressed={view === "gallery"}
      >
        <LayoutGrid className="h-4 w-4" />
        Gallery
      </button>
      <button
        type="button"
        onClick={() => onChange("list")}
        className={cn(
          "flex items-center gap-2 rounded-xl px-4 py-2 text-sm font-medium transition",
          view === "list"
            ? "bg-white text-brand-700 shadow-sm"
            : "text-slate-500 hover:text-slate-700",
        )}
        aria-label="List view"
        aria-pressed={view === "list"}
      >
        <List className="h-4 w-4" />
        List
      </button>
    </div>
  );
}