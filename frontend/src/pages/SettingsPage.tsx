import { useState } from 'react';

export function SettingsPage() {
  const [autoSync, setAutoSync] = useState(true);
  const [localOnly, setLocalOnly] = useState(true);
  const [chunkSize, setChunkSize] = useState('512');
  const [chunkOverlap, setChunkOverlap] = useState('50');

  return (
    <div className="flex flex-col gap-stack-md">
      <div className="mb-stack-lg">
        <h2 className="text-display text-on-surface mb-2">Settings</h2>
        <p className="text-body-lg text-on-surface-variant">
          Configure indexing, privacy and runtime options.
        </p>
      </div>

      {/* Indexing settings */}
      <div className="glass-card rounded-xl p-6 shadow-sm flex flex-col gap-6">
        <div className="flex items-center gap-3 pb-4 border-b border-outline-variant/20">
          <span className="material-symbols-outlined text-on-surface-variant">tune</span>
          <h3 className="text-headline-md">Indexing</h3>
        </div>

        <div className="grid gap-6 md:grid-cols-2">
          <div>
            <label className="block text-label-caps font-label-caps text-outline uppercase mb-1.5">
              Chunk Size (tokens)
            </label>
            <input
              type="number"
              value={chunkSize}
              onChange={(e) => setChunkSize(e.target.value)}
              className="w-full px-4 py-2.5 bg-surface-container rounded-lg border border-outline-variant/30 text-body-md text-on-surface outline-none focus:border-primary focus:ring-2 focus:ring-primary/10 transition"
            />
          </div>
          <div>
            <label className="block text-label-caps font-label-caps text-outline uppercase mb-1.5">
              Chunk Overlap (tokens)
            </label>
            <input
              type="number"
              value={chunkOverlap}
              onChange={(e) => setChunkOverlap(e.target.value)}
              className="w-full px-4 py-2.5 bg-surface-container rounded-lg border border-outline-variant/30 text-body-md text-on-surface outline-none focus:border-primary focus:ring-2 focus:ring-primary/10 transition"
            />
          </div>
        </div>

        {/* Toggle rows */}
        {[
          { label: 'Auto-sync on file change', sub: 'Re-index when files in the repo are saved.', value: autoSync, set: setAutoSync },
          { label: 'Local-only mode', sub: 'All data stays on this machine — nothing leaves.', value: localOnly, set: setLocalOnly },
        ].map((row) => (
          <div key={row.label} className="flex items-center justify-between py-2 border-b border-outline-variant/10 last:border-0">
            <div>
              <p className="text-body-md font-semibold text-on-surface">{row.label}</p>
              <p className="text-body-sm text-on-surface-variant">{row.sub}</p>
            </div>
            <button
              type="button"
              role="switch"
              aria-checked={row.value}
              onClick={() => row.set((v: boolean) => !v)}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                row.value ? 'bg-primary' : 'bg-outline-variant'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  row.value ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>
        ))}
      </div>

      {/* Save button */}
      <div className="flex justify-end">
        <button
          type="button"
          className="flex items-center gap-2 px-6 py-2.5 bg-primary text-on-primary rounded-lg font-semibold hover:bg-primary/90 transition-all active:scale-95 text-body-md"
        >
          <span className="material-symbols-outlined text-lg">save</span>
          Save Settings
        </button>
      </div>
    </div>
  );
}
