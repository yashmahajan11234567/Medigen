export function AboutCard() {
  return (
    <div className="rounded-3xl border border-slate-100 bg-white p-5 shadow-soft sm:p-6">
      <h3 className="mb-4 text-base font-semibold text-slate-900">About MediGen</h3>
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-sm text-slate-500">Application Version</span>
          <span className="text-sm font-semibold text-slate-900">v1.0.0</span>
        </div>
        <div className="flex items-center justify-between border-t border-slate-50 pt-3">
          <span className="text-sm text-slate-500">Build Version</span>
          <span className="text-sm font-semibold text-slate-900">2026.07.18</span>
        </div>
        <div className="flex items-center justify-between border-t border-slate-50 pt-3">
          <span className="text-sm text-slate-500">Developer</span>
          <span className="text-sm font-semibold text-slate-900">MediGen Team</span>
        </div>
        <div className="flex items-center justify-between border-t border-slate-50 pt-3">
          <span className="text-sm text-slate-500">License</span>
          <span className="text-sm font-semibold text-slate-900">MIT</span>
        </div>
      </div>
    </div>
  );
}