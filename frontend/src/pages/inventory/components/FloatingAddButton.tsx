import { Plus } from "lucide-react";

interface FloatingAddButtonProps {
  onClick: () => void;
}

export function FloatingAddButton({ onClick }: FloatingAddButtonProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="fixed bottom-24 right-6 z-30 flex items-center gap-2 rounded-2xl bg-brand-500 px-5 py-3.5 text-sm font-semibold text-white shadow-lg shadow-brand-300 transition hover:bg-brand-600 active:scale-95 lg:bottom-8"
    >
      <Plus className="h-5 w-5" />
      <span>Add Medicine</span>
    </button>
  );
}