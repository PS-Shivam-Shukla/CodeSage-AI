export function VectorStorePage() {
  const stats = [
    { icon: 'storage',     label: 'Vector DB',   value: 'ChromaDB',  sub: 'Local instance' },
    { icon: 'view_agenda', label: 'Total Chunks', value: '543',       sub: 'From last index' },
    { icon: 'hub',         label: 'Collections', value: '1',         sub: 'Active' },
    { icon: 'memory',      label: 'Index Size',  value: '~48 MB',    sub: 'On disk' },
  ];

  return (
    <div className="flex flex-col gap-stack-md">
      <div className="mb-stack-lg">
        <h2 className="text-display text-on-surface mb-2">Vector Store</h2>
        <p className="text-body-lg text-on-surface-variant">
          Inspect and manage your ChromaDB vector store.
        </p>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-stack-md">
        {stats.map((s) => (
          <div key={s.label} className="glass-card rounded-xl p-5 flex flex-col gap-2 shadow-sm">
            <span className="material-symbols-outlined text-primary">{s.icon}</span>
            <p className="text-body-sm text-on-surface-variant">{s.label}</p>
            <p className="text-headline-md text-on-surface">{s.value}</p>
            <p className="text-body-sm text-outline">{s.sub}</p>
          </div>
        ))}
      </div>

      {/* Placeholder action area */}
      <div className="glass-card rounded-xl p-6 shadow-sm flex items-start gap-4">
        <div className="w-9 h-9 bg-primary/10 text-primary rounded-lg flex items-center justify-center shrink-0">
          <span className="material-symbols-outlined">hub</span>
        </div>
        <div>
          <h3 className="text-headline-md mb-1">Collection Management</h3>
          <p className="text-body-md text-on-surface-variant mb-4">
            Full collection inspection and deletion controls will be available here.
          </p>
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-tertiary-fixed text-on-tertiary-fixed text-xs font-bold uppercase tracking-wide">
            <span className="w-1.5 h-1.5 rounded-full bg-tertiary" />
            Coming soon
          </span>
        </div>
      </div>
    </div>
  );
}
