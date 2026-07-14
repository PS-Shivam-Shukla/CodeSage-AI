const SAMPLE_LOGS = [
  { level: 'INFO',  time: '10:42:01', message: 'FastAPI application started successfully.' },
  { level: 'INFO',  time: '10:42:03', message: 'ChromaDB connected at ./chroma_db' },
  { level: 'INFO',  time: '10:43:15', message: 'Indexing started for: C:\\Users\\Shivam\\Desktop\\SpringBoot-App' },
  { level: 'INFO',  time: '10:45:49', message: 'Indexed 128 files — 543 chunks created.' },
  { level: 'INFO',  time: '10:46:02', message: 'RAG pipeline ready.' },
  { level: 'DEBUG', time: '10:47:11', message: 'Received chat request: "How does JWT authentication work?"' },
  { level: 'INFO',  time: '10:47:14', message: 'Retrieved 5 relevant chunks from vector store.' },
  { level: 'INFO',  time: '10:47:19', message: 'LLM response generated in 5.2s.' },
];

const LEVEL_STYLE: Record<string, string> = {
  INFO:  'text-secondary bg-secondary-container/40',
  DEBUG: 'text-on-surface-variant bg-surface-container',
  WARN:  'text-on-error-container bg-error-container/40',
  ERROR: 'text-error bg-error-container/40',
};

export function LogsPage() {
  return (
    <div className="flex flex-col gap-stack-md">
      <div className="mb-stack-lg">
        <h2 className="text-display text-on-surface mb-2">Logs</h2>
        <p className="text-body-lg text-on-surface-variant">
          Live application and indexing logs from the backend.
        </p>
      </div>

      <div className="glass-card rounded-xl shadow-sm overflow-hidden">
        <div className="p-4 border-b border-outline-variant/20 flex items-center gap-3 bg-surface-container-low/50">
          <span className="material-symbols-outlined text-on-surface-variant">terminal</span>
          <h3 className="text-headline-md">Application Logs</h3>
          <span className="ml-auto flex items-center gap-1.5 text-body-sm text-secondary font-semibold">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-secondary opacity-75" />
              <span className="relative inline-flex rounded-full h-2 w-2 bg-secondary" />
            </span>
            Live
          </span>
        </div>

        <div className="p-4 font-code-snippet text-code-snippet space-y-1 custom-scrollbar max-h-[520px] overflow-y-auto bg-surface-container-lowest">
          {SAMPLE_LOGS.map((log, i) => (
            <div key={i} className="flex items-start gap-3 py-1">
              <span className="text-outline shrink-0 w-16">{log.time}</span>
              <span
                className={`shrink-0 px-1.5 py-0.5 rounded text-[10px] font-bold uppercase ${LEVEL_STYLE[log.level] ?? ''}`}
              >
                {log.level}
              </span>
              <span className="text-on-surface break-all">{log.message}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
