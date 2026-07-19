import { FolderCard } from "@/pages/medical-records/components/FolderCard";

const folders = [
  { name: "Fever", count: 4 },
  { name: "Diabetes", count: 6 },
  { name: "Blood Pressure", count: 3 },
  { name: "Heart", count: 2 },
  { name: "Dental", count: 5 },
  { name: "Eye Care", count: 3 },
  { name: "General", count: 8 },
];

export function FolderGrid() {
  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-7">
      {folders.map((f) => (
        <FolderCard key={f.name} name={f.name} count={f.count} />
      ))}
    </div>
  );
}