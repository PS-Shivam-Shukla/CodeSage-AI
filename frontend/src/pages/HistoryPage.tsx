export function HistoryPage() {
  return (
    <div className="flex flex-col gap-stack-md">
      <div className="mb-stack-lg">
        <h2 className="text-display text-on-surface mb-2">History</h2>
        <p className="text-body-lg text-on-surface-variant">
          Review your past conversations and indexing sessions.
        </p>
      </div>

      <div className="glass-card rounded-xl p-8 flex flex-col items-center justify-center min-h-[320px] text-center gap-4">
        <span
          className="material-symbols-outlined text-outline"
          style={{ fontSize: '48px', fontVariationSettings: "'FILL' 0" }}
        >
          history
        </span>
        <p className="text-headline-md text-on-surface-variant">No history yet</p>
        <p className="text-body-md text-outline max-w-sm">
          Your conversation history and past indexing runs will appear here.
        </p>
      </div>
    </div>
  );
}
