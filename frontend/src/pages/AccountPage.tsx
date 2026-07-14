export function AccountPage() {
  return (
    <div className="flex flex-col gap-stack-md">
      <div className="mb-stack-lg">
        <h2 className="text-display text-on-surface mb-2">Account</h2>
        <p className="text-body-lg text-on-surface-variant">
          Manage your profile and preferences.
        </p>
      </div>

      <div className="glass-card rounded-xl p-6 shadow-sm flex flex-col gap-6">
        {/* Avatar + name */}
        <div className="flex items-center gap-5 pb-6 border-b border-outline-variant/20">
          <div className="w-16 h-16 rounded-full bg-primary-container flex items-center justify-center text-on-primary-container">
            <span
              className="material-symbols-outlined"
              style={{ fontSize: '32px', fontVariationSettings: "'FILL' 1" }}
            >
              person
            </span>
          </div>
          <div>
            <p className="text-headline-md text-on-surface">Local User</p>
            <p className="text-body-md text-on-surface-variant">Running in local-only mode</p>
          </div>
        </div>

        {/* Profile fields (read-only in local mode) */}
        <div className="grid gap-4 md:grid-cols-2">
          {[
            { label: 'Display Name', value: 'Local User' },
            { label: 'Mode', value: 'Local Only' },
            { label: 'Version', value: 'v2.4.0-stable' },
            { label: 'Backend URL', value: 'http://localhost:8000' },
          ].map((f) => (
            <div key={f.label}>
              <label className="block text-label-caps font-label-caps text-outline uppercase mb-1.5">
                {f.label}
              </label>
              <div className="px-4 py-2.5 bg-surface-container rounded-lg border border-outline-variant/30 text-body-md text-on-surface-variant font-code-snippet">
                {f.value}
              </div>
            </div>
          ))}
        </div>

        {/* Sign out */}
        <div className="flex justify-end pt-2">
          <button
            type="button"
            className="flex items-center gap-2 px-4 py-2 text-error hover:bg-error-container/20 border border-error/20 rounded-lg text-body-md font-semibold transition-all active:scale-95"
          >
            <span className="material-symbols-outlined text-lg">logout</span>
            Sign Out
          </button>
        </div>
      </div>
    </div>
  );
}
