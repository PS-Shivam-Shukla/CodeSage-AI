import { useState } from 'react';

interface KeyRow {
  name: string;
  masked: string;
  created: string;
}

const SAMPLE_KEYS: KeyRow[] = [
  { name: 'Together AI',  masked: 'sk-•••••••••••••••••••••••••••••12ab', created: 'Oct 10, 2024' },
  { name: 'OpenAI (fallback)', masked: 'sk-•••••••••••••••••••••••••••••99cd', created: 'Sep 22, 2024' },
];

export function ApiKeysPage() {
  const [showForm, setShowForm] = useState(false);

  return (
    <div className="flex flex-col gap-stack-md">
      <div className="mb-stack-lg flex items-start justify-between">
        <div>
          <h2 className="text-display text-on-surface mb-2">API Keys</h2>
          <p className="text-body-lg text-on-surface-variant">
            Manage your LLM provider API keys. Keys are stored locally.
          </p>
        </div>
        <button
          type="button"
          onClick={() => setShowForm((v) => !v)}
          className="flex items-center gap-2 px-4 py-2 bg-primary text-on-primary rounded-lg font-semibold hover:bg-primary/90 transition-all active:scale-95 text-body-md shrink-0"
        >
          <span className="material-symbols-outlined text-lg">add</span>
          Add Key
        </button>
      </div>

      {/* Add key form */}
      {showForm && (
        <div className="glass-card rounded-xl p-6 shadow-sm flex flex-col gap-4">
          <h3 className="text-headline-md">New API Key</h3>
          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <label className="block text-label-caps font-label-caps text-outline uppercase mb-1.5">
                Provider Name
              </label>
              <input
                type="text"
                placeholder="e.g. Together AI"
                className="w-full px-4 py-2.5 bg-surface-container rounded-lg border border-outline-variant/30 text-body-md text-on-surface outline-none focus:border-primary focus:ring-2 focus:ring-primary/10 transition"
              />
            </div>
            <div>
              <label className="block text-label-caps font-label-caps text-outline uppercase mb-1.5">
                API Key
              </label>
              <input
                type="password"
                placeholder="sk-••••••••••••••••••••••"
                className="w-full px-4 py-2.5 bg-surface-container rounded-lg border border-outline-variant/30 text-body-md text-on-surface outline-none focus:border-primary focus:ring-2 focus:ring-primary/10 transition font-code-snippet"
              />
            </div>
          </div>
          <div className="flex gap-3 justify-end">
            <button
              type="button"
              onClick={() => setShowForm(false)}
              className="px-4 py-2 text-on-surface-variant hover:bg-surface-container-high rounded-lg text-body-md transition"
            >
              Cancel
            </button>
            <button
              type="button"
              className="px-4 py-2 bg-primary text-on-primary rounded-lg font-semibold hover:bg-primary/90 text-body-md transition active:scale-95"
            >
              Save Key
            </button>
          </div>
        </div>
      )}

      {/* Keys list */}
      <div className="glass-card rounded-xl shadow-sm overflow-hidden">
        <div className="p-5 border-b border-outline-variant/20 flex items-center gap-3">
          <span className="material-symbols-outlined text-on-surface-variant">key</span>
          <h3 className="text-headline-md">Saved Keys</h3>
        </div>
        <div className="divide-y divide-outline-variant/10">
          {SAMPLE_KEYS.map((k) => (
            <div key={k.name} className="flex items-center justify-between px-6 py-4 hover:bg-surface-container/40 transition-colors">
              <div>
                <p className="text-body-md font-semibold text-on-surface">{k.name}</p>
                <p className="text-body-sm font-code-snippet text-on-surface-variant mt-0.5">{k.masked}</p>
              </div>
              <div className="flex items-center gap-4">
                <span className="text-body-sm text-outline">{k.created}</span>
                <button
                  type="button"
                  className="p-1.5 text-error hover:bg-error-container/20 rounded-lg transition-colors"
                  title="Delete key"
                >
                  <span className="material-symbols-outlined" style={{ fontSize: '18px' }}>delete</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
