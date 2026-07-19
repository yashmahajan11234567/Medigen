import { cn } from "@/lib/cn";

interface Category {
  id: string;
  label: string;
  count: number;
  icon: string;
}

interface CategorySidebarProps {
  selected: string;
  onSelect: (id: string) => void;
  categories: Category[];
}

export function CategorySidebar({
  selected,
  onSelect,
  categories,
}: CategorySidebarProps) {
  return (
    <aside className="hidden w-56 shrink-0 lg:block">
      <nav className="space-y-1">
        {categories.map((cat) => (
          <button
            key={cat.id}
            type="button"
            onClick={() => onSelect(cat.id)}
            className={cn(
              "flex w-full items-center gap-3 rounded-2xl px-4 py-3 text-left text-sm font-medium transition",
              selected === cat.id
                ? "bg-brand-50 text-brand-700 shadow-sm"
                : "text-slate-600 hover:bg-slate-50 hover:text-slate-900",
            )}
          >
            <span className="text-lg">{cat.icon}</span>
            <span className="flex-1">{cat.label}</span>
            <span
              className={cn(
                "rounded-full px-2.5 py-0.5 text-xs",
                selected === cat.id
                  ? "bg-brand-100 text-brand-700"
                  : "bg-slate-100 text-slate-500",
              )}
            >
              {cat.count}
            </span>
          </button>
        ))}
      </nav>
    </aside>
  );
}

export function CategoryChips({
  selected,
  onSelect,
  categories,
}: {
  selected: string;
  onSelect: (id: string) => void;
  categories: Category[];
}) {
  return (
    <div className="flex gap-2 overflow-x-auto pb-1 lg:hidden">
      {categories.map((cat) => (
        <button
          key={cat.id}
          type="button"
          onClick={() => onSelect(cat.id)}
          className={cn(
            "flex shrink-0 items-center gap-1.5 rounded-full px-4 py-2 text-sm font-medium transition",
            selected === cat.id
              ? "bg-brand-500 text-white shadow-sm"
              : "bg-slate-100 text-slate-600 hover:bg-slate-200",
          )}
        >
          <span>{cat.icon}</span>
          <span>{cat.label}</span>
          <span
            className={cn(
              "ml-0.5 rounded-full px-1.5 text-xs",
              selected === cat.id ? "bg-brand-400" : "bg-slate-200 text-slate-500",
            )}
          >
            {cat.count}
          </span>
        </button>
      ))}
    </div>
  );
}