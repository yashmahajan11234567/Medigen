import { Outlet } from "react-router-dom";
import { Header } from "@/components/layout/Header";
import { MobileNav } from "@/components/layout/MobileNav";
import { Sidebar } from "@/components/layout/Sidebar";

export function AppShell() {
  return (
    <div className="min-h-screen bg-health-grid">
      <div className="mx-auto flex min-h-screen max-w-[1600px] gap-6 px-4 py-4 sm:px-6 lg:px-8">
        <Sidebar />
        <div className="flex min-h-[calc(100vh-2rem)] flex-1 flex-col rounded-[2rem] border border-white/70 bg-slate-50/85 shadow-soft">
          <Header />
          <main className="flex-1 px-4 pb-24 pt-6 sm:px-6 lg:px-8">
            <Outlet />
          </main>
          <MobileNav />
        </div>
      </div>
    </div>
  );
}
