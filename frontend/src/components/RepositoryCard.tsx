import { useRef } from 'react';
import { Button } from '@/components/ui/button';

interface StatusRow {
  icon: string;
  label: string;
  value: string;
  valueClass?: string;
}

const STATUS_ROWS: StatusRow[] = [
  { icon: 'account_tree',  label: 'Repository',     value: 'SpringBoot-App' },
  { icon: 'description',   label: 'Files',          value: '128' },
  { icon: 'view_agenda',   label: 'Chunks',         value: '543' },
  { icon: 'psychology',    label: 'Embedding Model',value: 'BAAI/bge-m3' },
  { icon: 'storage',       label: 'Vector DB',      value: 'ChromaDB', valueClass: 'text-primary' },
  { icon: 'smart_toy',     label: 'LLM',            value: 'Meta Llama 3.1 70B' },
  { icon: 'calendar_today',label: 'Last Indexed',   value: 'Oct 24, 2024' },
  { icon: 'memory',        label: 'RAM Usage',      value: '1.2 GB' },
  { icon: 'cloud_sync',    label: 'Sync Status',    value: 'Auto-Enabled' },
  { icon: 'lock',          label: 'Privacy',        value: 'Local Only' },
];

interface RepositoryCardProps {
  repoPath: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  loading: boolean;
  success: boolean;
  error?: string;
}

export function RepositoryCard({
  repoPath,
  onChange,
  onSubmit,
  loading,
  success,
  error,
}: RepositoryCardProps) {
  const inputRef = useRef<HTMLInputElement>(null);

  return (
    <div className="flex flex-col gap-stack-md">
      {/* ── Repository Setup ───────────────────────────────────────────── */}
      <div className="glass-card p-6 rounded-xl shadow-sm">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 bg-primary/10 text-primary rounded-lg flex items-center justify-center">
            <span
              className="material-symbols-outlined"
              style={{ fontVariationSettings: "'FILL' 1" }}
            >
              folder
            </span>
          </div>
          <h3 className="text-headline-md">Repository</h3>
        </div>

        <div className="space-y-4">
          {/* Path input */}
          <div>
            <label className="block text-label-caps font-label-caps text-outline uppercase mb-1.5 px-1">
              Source Path
            </label>
            <div className="flex items-center gap-2">
              <div className="flex-1 flex items-center gap-3 px-4 py-2.5 bg-surface-container rounded-lg border border-outline-variant/30">
                <span className="material-symbols-outlined text-outline">terminal</span>
                <input
                  ref={inputRef}
                  type="text"
                  value={repoPath}
                  onChange={(e) => onChange(e.target.value)}
                  placeholder="C:\Projects\MyApp"
                  className="bg-transparent border-none p-0 focus:ring-0 text-body-md font-code-snippet w-full text-on-surface-variant outline-none placeholder:text-outline/60"
                />
              </div>
              <button
                type="button"
                title="Browse folder"
                className="p-2.5 bg-surface-container hover:bg-surface-container-high border border-outline-variant/30 rounded-lg transition-colors"
              >
                <span className="material-symbols-outlined">folder_open</span>
              </button>
            </div>
          </div>

          {/* Index button */}
          <Button
            onClick={onSubmit}
            disabled={loading}
            className="w-full justify-center py-3 rounded-lg"
          >
            <span className="material-symbols-outlined text-lg">sync</span>
            {loading ? 'Indexing…' : 'Index Repository'}
          </Button>
        </div>
      </div>

      {/* ── Success / Error Alert ──────────────────────────────────────── */}
      {(success || error) && (
        <div
          className={`border p-4 rounded-xl flex items-start gap-4 ${
            error
              ? 'bg-error-container/40 border-error/20'
              : 'bg-secondary-container/50 border-secondary/20'
          }`}
        >
          <div className="mt-0.5">
            <span
              className={`material-symbols-outlined ${error ? 'text-error' : 'text-secondary'}`}
              style={{ fontVariationSettings: "'FILL' 1" }}
            >
              {error ? 'error' : 'check_circle'}
            </span>
          </div>
          <div>
            <p
              className={`font-semibold text-body-md ${
                error ? 'text-error' : 'text-on-secondary-container'
              }`}
            >
              {error ?? 'Indexed successfully'}
            </p>
            {!error && (
              <div className="flex gap-3 mt-1">
                <span className="text-xs font-code-snippet text-on-secondary-container/70">128 files</span>
                <span className="text-xs text-on-secondary-container/30">•</span>
                <span className="text-xs font-code-snippet text-on-secondary-container/70">543 chunks</span>
                <span className="text-xs text-on-secondary-container/30">•</span>
                <span className="text-xs font-code-snippet text-on-secondary-container/70">2m 34s</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* ── Repository Status ──────────────────────────────────────────── */}
      <div className="glass-card p-6 rounded-xl shadow-sm">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-headline-md">Repository Status</h3>
          <span className="px-3 py-1 bg-secondary-container text-on-secondary-container text-xs font-bold rounded-full uppercase tracking-wider flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-secondary" />
            Indexed
          </span>
        </div>

        <div className="space-y-0.5">
          {STATUS_ROWS.map((row, i) => (
            <div
              key={row.label}
              className={`flex justify-between py-2 ${
                i < STATUS_ROWS.length - 1 ? 'border-b border-outline-variant/10' : ''
              }`}
            >
              <div className="flex items-center gap-2 text-on-surface-variant">
                <span className="material-symbols-outlined text-sm">{row.icon}</span>
                <span className="text-body-sm font-medium">{row.label}</span>
              </div>
              <span
                className={`text-body-sm font-code-snippet ${row.valueClass ?? ''}`}
              >
                {row.value}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
